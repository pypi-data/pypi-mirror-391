import json
from pathlib import Path
from typing import Dict

# New flat symbol map: iri -> identifier
SymbolMap = Dict[str, str]


def load_symbol_map(path: Path) -> SymbolMap:
    """Load a persisted symbol map from JSON if present; else return an empty flat map.

    New format (preferred):
      { "<iri>": "identifier", ... }

    Backward compatible with legacy nested format (by kind):
      { "classes": {"<iri>": "identifier", ...}, "object_properties": {…}, ... }
    In that case, all entries are merged into a single flat map; if the same IRI
    appears in multiple sections with different identifiers, the first encountered
    value by a deterministic section order is kept.
    """
    if not path.exists():
        return {}
    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return {}

    # If already flat: map of iri -> identifier (strings)
    if isinstance(data, dict) and all(isinstance(v, str) for v in data.values()):
        return {str(iri): str(ident) for iri, ident in data.items()}

    # Legacy nested format: kind -> {iri -> identifier}
    flat: SymbolMap = {}
    if isinstance(data, dict):
        # deterministic section order
        section_order = [
            "classes",
            "object_properties",
            "data_properties",
            "individuals",
            "annotation_properties",
        ]
        # Add any other sections at the end deterministically
        others = [k for k in sorted(data.keys()) if k not in section_order]
        for section in section_order + others:
            sec = data.get(section)
            if isinstance(sec, dict):
                for iri, ident in sec.items():
                    iri_s = str(iri)
                    if iri_s not in flat:
                        flat[iri_s] = str(ident)
    return flat


def save_symbol_map(path: Path, smap: SymbolMap) -> None:
    """Persist the symbol map to JSON in the flat format with stable ordering and UTF-8 encoding."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(smap, f, indent=2, ensure_ascii=False, sort_keys=True)
