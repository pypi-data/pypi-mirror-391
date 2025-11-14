import keyword
import re
from typing import Dict, List, Tuple

from nl.newfoundland.kgworkflow.generator.iri.discovery import (
    K_CLASS,
    K_OBJECT_PROPERTY,
    K_DATA_PROPERTY,
    K_INDIVIDUAL,
    K_ANNOTATION_PROPERTY,
)
from nl.newfoundland.kgworkflow.generator.iri.symbol_map import SymbolMap

_KIND_SUFFIX = {
    K_CLASS: "_cls",
    K_OBJECT_PROPERTY: "_op",
    K_DATA_PROPERTY: "_dp",
    K_INDIVIDUAL: "_ind",
    K_ANNOTATION_PROPERTY: "_ann",
}


def _to_snake(name: str) -> str:
    """Convert an arbitrary string to a safe snake_case Python identifier."""
    name = re.sub(r"[^0-9A-Za-z_]+", "_", name)
    name = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name)
    name = name.lower()
    name = re.sub(r"_{2,}", "_", name).strip("_")
    if not name:
        name = "symbol"
    if name[0].isdigit():
        name = f"_{name}"
    return name


def _to_camel(name: str) -> str:
    """Convert an arbitrary string to a lowerCamelCase Python identifier."""
    # Robust lowerCamelCase conversion from mixed-case/sep words
    # 1) Normalize separators to spaces (treat underscore as separator too)
    s = re.sub(r"[^0-9A-Za-z]+", " ", name)
    s = s.replace("_", " ")
    # 2) Split CamelCase boundaries to words as well
    s = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", s)
    parts = [p for p in s.split() if p]
    if not parts:
        return "symbol"
    head = parts[0].lower()
    rest = [p[:1].upper() + p[1:].lower() if p else "" for p in parts[1:]]
    return head + "".join(rest)


def _sanitize_identifier(raw: str, style: str, kind: str) -> str:
    # Base conversion
    if style in ("camel", "custom"):
        ident = _to_camel(raw)
        # For custom, adjust capitalization for classes now
        if style == "custom" and kind == K_CLASS and ident:
            ident = ident[:1].upper() + ident[1:]
    else:
        ident = _to_snake(raw)
    # Avoid Python reserved words and invalid leading digits
    if keyword.iskeyword(ident) or ident in {"None", "True", "False"}:
        ident = ident + "_"
    if ident and ident[0].isdigit():
        ident = "_" + ident
    # For custom style, ensure individuals end with a single underscore
    if style == "custom" and kind == K_INDIVIDUAL and not ident.endswith("_"):
        ident = ident + "_"
    return ident


def _base_name_from(iri: str) -> str:
    if "#" in iri:
        return iri.rsplit("#", 1)[-1]
    return iri.rstrip("/").rsplit("/", 1)[-1]


def assign_names(enriched: Dict[str, Dict[str, dict]], cfg, symbol_map: SymbolMap):
    """Assign stable Python identifiers to IRIs across all kinds.

    Strategy:
    - Prefer persisted names from the provided symbol_map for stability.
    - Else, derive from preferred label (or local IRI name) and sanitize per style.
    - Resolve cross-kind collisions by appending kind-specific suffixes.
    - Resolve within-kind collisions by adding deterministic numeric counters.
    - Return (assigned, new_symbol_map, diagnostics).
    """
    # Load existing names for stability (flat map: iri -> identifier)
    existing = symbol_map.copy()

    assigned: Dict[str, Dict[str, dict]] = {k: {} for k in enriched.keys()}
    collisions: Dict[str, List[Tuple[str, str]]] = {}

    # First pass: propose base identifiers
    proposals: Dict[str, Dict[str, str]] = {k: {} for k in enriched.keys()}
    for kind, items in enriched.items():
        for iri, info in items.items():
            # Prefer persisted name (flat map: iri -> identifier)
            if iri in existing:
                ident = existing[iri]
                # If the persisted name looks like a placeholder from an earlier run,
                # recompute a better name from labels/local name to conform to the plan.
                if re.fullmatch(r"none_(cls|op|dp|ind|ann)_\d+", ident):
                    pref = info.get("preferred_label")
                    if isinstance(pref, str) and pref.strip().lower() != "none" and pref.strip() != "":
                        raw = pref
                    else:
                        raw = _base_name_from(iri)
                    ident = _sanitize_identifier(raw, cfg.symbol_style, kind)
            else:
                pref = info.get("preferred_label")
                # Some datasets may contain the literal string "None"; treat it as missing
                if isinstance(pref, str) and pref.strip().lower() != "none" and pref.strip() != "":
                    raw = pref
                else:
                    raw = _base_name_from(iri)
                ident = _sanitize_identifier(raw, cfg.symbol_style, kind)
            proposals[kind][iri] = ident

    # Cross-kind collisions: collect all identifiers across kinds
    all_to_kind_iris: Dict[str, List[Tuple[str, str]]] = {}
    for kind, m in proposals.items():
        for iri, ident in m.items():
            all_to_kind_iris.setdefault(ident, []).append((kind, iri))

    # Apply suffix for cross-kind collisions
    resolved: Dict[str, Dict[str, str]] = {k: {} for k in enriched.keys()}
    for ident, pairs in all_to_kind_iris.items():
        if len(pairs) == 1:
            kind, iri = pairs[0]
            resolved[kind][iri] = ident
        else:
            for kind, iri in pairs:
                resolved[kind][iri] = ident + _KIND_SUFFIX[kind]

    # Within-kind collisions: add numeric counters deterministically
    final_names: Dict[str, Dict[str, str]] = {k: {} for k in enriched.keys()}
    for kind, m in resolved.items():
        reverse: Dict[str, List[str]] = {}
        for iri, ident in m.items():
            reverse.setdefault(ident, []).append(iri)
        for ident, iris in reverse.items():
            if len(iris) == 1:
                final_names[kind][iris[0]] = ident
            else:
                for i, iri in enumerate(sorted(iris)):
                    final_names[kind][iri] = f"{ident}_{i + 1}"
                collisions.setdefault(kind, []).append((ident, f"{len(iris)} items"))

    # Persist into symbol_map (flat: iri -> identifier)
    new_symbol_map: SymbolMap = {}
    for kind, m in final_names.items():
        for iri, ident in m.items():
            new_symbol_map[iri] = ident

    # Build assignments output, merge back enriched info and assigned names
    for kind, items in enriched.items():
        for iri, info in items.items():
            assigned[kind][info["iri"]] = {
                **info,
                "identifier": final_names[kind][iri],
            }

    naming_diag = {
        "collisions": collisions,
        "persisted_count": sum(
            1 for k in enriched.keys() for iri in enriched[k].keys() if iri in symbol_map
        ),
    }

    return assigned, new_symbol_map, naming_diag
