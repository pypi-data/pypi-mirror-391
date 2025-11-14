import logging
from typing import Dict, List, Set, Tuple

from nl.newfoundland.kgworkflow.generator.iri import manchester as m
from nl.newfoundland.kgworkflow.generator.iri.discovery import (
    K_CLASS,
    K_OBJECT_PROPERTY,
    K_DATA_PROPERTY,
    K_INDIVIDUAL,
)

PREFIX = """
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX dc: <http://purl.org/dc/terms/>
PREFIX dc11: <http://purl.org/dc/elements/1.1/>
PREFIX IAO: <http://purl.obolibrary.org/obo/IAO_>
"""


# --- Utility helpers for batching ------------------------------------------------------

def _is_valid_iri(iri: str) -> bool:
    """Return True if the given string looks like a valid absolute IRI.

    Filters out empty strings and the literal "None" (case-insensitive) to
    prevent generating invalid SPARQL VALUES like `<None>`.
    """
    if not isinstance(iri, str):
        return False
    s = iri.strip()
    if not s or s.lower() == "none":
        return False
    return s.startswith("http://") or s.startswith("https://") or s.startswith("urn:")

def _chunk(seq: List[str], size: int) -> List[List[str]]:
    return [seq[i : i + size] for i in range(0, len(seq), size)]


def _sort_lang(vals: List[Tuple[str, str]], lang_prefs: List[str]) -> List[Tuple[str, str]]:
    pref_index = {lang: i for i, lang in enumerate(lang_prefs)}
    return sorted(vals, key=lambda t: (pref_index.get(t[1], 999), t[0]))


# --- Original per-IRI helpers (kept for reference and potential reuse) -----------------

def _labels_for(graph, backend, iri: str, lang_prefs: List[str]) -> Dict[str, List[Tuple[str, str]]]:
    """Return labels for a single IRI grouped by predicate IRI.

    The results are ordered by language preference (then lexicographically) via
    SPARQL to minimize Python-side work.
    """
    if not _is_valid_iri(iri):
        return {}
    # Order results by language preference in SPARQL to avoid Python-side sorting
    values_lang = " ".join(f"(\"{lp}\" {i})" for i, lp in enumerate(lang_prefs))
    q = f"""
    SELECT ?p ?l ?lang ?r WHERE {{
      VALUES ?s {{ <{iri}> }}
      ?s ?p ?lit .
      FILTER(?p IN (<http://www.w3.org/2000/01/rdf-schema#label>, <http://www.w3.org/2004/02/skos/core#prefLabel>, <http://www.w3.org/2004/02/skos/core#altLabel>))
      BIND(STR(?lit) AS ?l)
      BIND(LANG(?lit) AS ?lang)
      OPTIONAL {{ VALUES (?pref ?rank) {{ {values_lang} }} FILTER(?lang = ?pref) }}
      BIND(COALESCE(?rank, 999) AS ?r)
    }}
    ORDER BY ?p ?r ?l
    """
    out: Dict[str, List[Tuple[str, str]]] = {}
    for row in backend.query(graph, PREFIX + q):
        p = str(row[0])
        l = str(row[1])
        lang = str(row[2]) if row[2] else ""
        out.setdefault(p, []).append((l, lang))
    return out


def _deprecated(graph, backend, iri: str) -> bool:
    """Return True if the IRI has `owl:deprecated true` in the graph."""
    q = f"""
    SELECT (COUNT(*) AS ?n) WHERE {{
      VALUES ?s {{ <{iri}> }}
      ?s owl:deprecated ?b .
      FILTER(?b = true || STR(?b) = "true")
    }}
    """
    for row in backend.query(graph, PREFIX + q):
        try:
            return int(row[0]) > 0
        except Exception:
            pass
    return False


def _annotations_for(graph, backend, iri: str, lang_prefs: List[str]):
    """Collect key annotations for a single IRI with language-ordered results.

    Returns a dict with optional single values for definition/comment/identifier
    (including the predicate IRI used) and lists for examples/scope_notes.
    """
    # Order by language preference in SPARQL to reduce Python work
    values_lang = " ".join(f"(\"{lp}\" {i})" for i, lp in enumerate(lang_prefs))
    q = f"""
    SELECT ?p ?val ?lang ?r WHERE {{
      VALUES ?s {{ <{iri}> }}
      VALUES ?p {{ rdfs:comment skos:definition skos:example skos:scopeNote dc:description dc11:identifier <http://purl.obolibrary.org/obo/IAO_0000115> }}
      ?s ?p ?lit .
      BIND(STR(?lit) AS ?val)
      BIND(LANG(?lit) AS ?lang)
      OPTIONAL {{ VALUES (?pref ?rank) {{ {values_lang} }} FILTER(?lang = ?pref) }}
      BIND(COALESCE(?rank, 999) AS ?r)
    }}
    ORDER BY ?p ?r ?val
    """
    collected: Dict[str, List[Tuple[str, str]]] = {}
    for row in backend.query(graph, PREFIX + q):
        p = str(row[0])
        v = str(row[1])
        lang = str(row[2]) if row[2] else ""
        collected.setdefault(p, []).append((v, lang))

    # Helper to pick first with provenance
    def pick_first(props: List[str]):
        for p in props:
            arr = collected.get(p)
            if arr:
                v, lg = arr[0]
                return (p, v, lg)
        return None

    definition = pick_first([
        "http://www.w3.org/2004/02/skos/core#definition",
        "http://purl.obolibrary.org/obo/IAO_0000115",
    ])
    comment = pick_first([
        "http://www.w3.org/2000/01/rdf-schema#comment",
        "http://purl.org/dc/terms/description",
    ])
    identifier = pick_first([
        "http://purl.org/dc/elements/1.1/identifier",
        "http://purl.org/dc/terms/identifier",
    ])
    # Examples and notes preserve their known source predicate
    examples_src = collected.get("http://www.w3.org/2004/02/skos/core#example", [])
    examples = [("http://www.w3.org/2004/02/skos/core#example", v, lg) for (v, lg) in examples_src]
    notes_src = collected.get("http://www.w3.org/2004/02/skos/core#scopeNote", [])
    notes = [("http://www.w3.org/2004/02/skos/core#scopeNote", v, lg) for (v, lg) in notes_src]
    return {
        "definition": definition,  # (predicate_iri, value, lang) or None
        "comment": comment,  # (predicate_iri, value, lang) or None
        "identifier": identifier,  # (predicate_iri, value, lang) or None (lang often empty)
        "examples": examples,  # list of (predicate_iri, value, lang)
        "scope_notes": notes,  # list of (predicate_iri, value, lang)
    }


# --- Batched helpers ------------------------------------------------------------------

def _labels_for_many(graph, backend, iris: List[str], lang_prefs: List[str]) -> Dict[str, Dict[str, List[Tuple[str, str]]]]:
    """Fetch labels for many IRIs in one SPARQL query.

    Returns a nested dict: subject IRI -> predicate IRI -> list of (value, lang),
    sorted by language preference and then lexicographically.
    """
    if not iris:
        return {}
    iris2 = [i for i in iris if _is_valid_iri(i)]
    if not iris2:
        return {}
    values = " ".join(f"<{i}>" for i in iris2)
    q = f"""
    SELECT ?s ?p ?l ?lang WHERE {{
      VALUES ?s {{ {values} }}
      VALUES ?p {{ <http://www.w3.org/2000/01/rdf-schema#label> <http://www.w3.org/2004/02/skos/core#prefLabel> <http://www.w3.org/2004/02/skos/core#altLabel> }}
      ?s ?p ?lit .
      BIND(STR(?lit) AS ?l)
      BIND(LANG(?lit) AS ?lang)
    }}
    """
    out: Dict[str, Dict[str, List[Tuple[str, str]]]] = {}
    for row in backend.query(graph, PREFIX + q):
        s = str(row[0])
        p = str(row[1])
        l = str(row[2])
        lang = str(row[3]) if row[3] else ""
        out.setdefault(s, {}).setdefault(p, []).append((l, lang))
    for s, preds in out.items():
        for p, vals in preds.items():
            preds[p] = _sort_lang(vals, lang_prefs)
    return out


def _deprecated_many(graph, backend, iris: List[str]) -> Dict[str, bool]:
    """Batch check `owl:deprecated` for many IRIs; returns a map IRI -> bool."""
    if not iris:
        return {}
    iris2 = [i for i in iris if _is_valid_iri(i)]
    if not iris2:
        return {}
    values = " ".join(f"<{i}>" for i in iris2)
    q = f"""
    SELECT ?s (COUNT(?b) AS ?n) WHERE {{
      VALUES ?s {{ {values} }}
      ?s owl:deprecated ?b .
      FILTER(?b = true || STR(?b) = "true")
    }} GROUP BY ?s
    """
    out = {i: False for i in iris2}
    for row in backend.query(graph, PREFIX + q):
        s = str(row[0])
        try:
            out[s] = int(row[1]) > 0
        except Exception:
            out[s] = False
    return out


def _annotations_for_many(graph, backend, iris: List[str], lang_prefs: List[str]):
    if not iris:
        return {}
    values = " ".join(f"<{i}>" for i in iris)
    q = f"""
    SELECT ?s ?p ?val ?lang WHERE {{
      VALUES ?s {{ {values} }}
      VALUES ?p {{ rdfs:comment skos:definition skos:example skos:scopeNote dc:description dc11:identifier <http://purl.obolibrary.org/obo/IAO_0000115> }}
      ?s ?p ?lit .
      BIND(STR(?lit) AS ?val)
      BIND(LANG(?lit) AS ?lang)
    }}
    """
    collected: Dict[str, Dict[str, List[Tuple[str, str]]]] = {}
    for row in backend.query(graph, PREFIX + q):
        s = str(row[0])
        p = str(row[1])
        v = str(row[2])
        lang = str(row[3]) if row[3] else ""
        collected.setdefault(s, {}).setdefault(p, []).append((v, lang))

    # Build per-IRI structured annotations matching _annotations_for output
    result: Dict[str, Dict[str, object]] = {}
    for s in iris:
        preds = collected.get(s, {})
        # Sort values per predicate by language preference
        for p, vals in preds.items():
            preds[p] = _sort_lang(vals, lang_prefs)

        def pick_first(props: List[str]):
            for p in props:
                arr = preds.get(p)
                if arr:
                    v, lg = arr[0]
                    return (p, v, lg)
            return None

        definition = pick_first([
            "http://www.w3.org/2004/02/skos/core#definition",
            "http://purl.obolibrary.org/obo/IAO_0000115",
        ])
        comment = pick_first([
            "http://www.w3.org/2000/01/rdf-schema#comment",
            "http://purl.org/dc/terms/description",
        ])
        identifier = pick_first([
            "http://purl.org/dc/elements/1.1/identifier",
            "http://purl.org/dc/terms/identifier",
        ])
        examples_src = preds.get("http://www.w3.org/2004/02/skos/core#example", [])
        examples = [("http://www.w3.org/2004/02/skos/core#example", v, lg) for (v, lg) in examples_src]
        notes_src = preds.get("http://www.w3.org/2004/02/skos/core#scopeNote", [])
        notes = [("http://www.w3.org/2004/02/skos/core#scopeNote", v, lg) for (v, lg) in notes_src]
        result[s] = {
            "definition": definition,
            "comment": comment,
            "identifier": identifier,
            "examples": examples,
            "scope_notes": notes,
        }
    return result


def enrich_entities(graph, discovered: Dict[str, Set[str]], cfg, backend):
    """Enrich discovered entities with labels, annotations, deprecation, and axioms.

    Batches SPARQL lookups to reduce round-trips; preserves language preference
    ordering and respects `cfg.max_axioms_per_entity` when limiting Manchester
    comments. Returns a nested dict: kind -> iri -> enriched info.
    """
    log = logging.getLogger("owl_to_python.enrich")
    total = sum(len(v) for v in discovered.values())
    processed = 0
    if total:
        log.info("Enrichment: %d entities", total)
    enriched: Dict[str, Dict[str, dict]] = {k: {} for k in discovered.keys()}
    for kind, iris in discovered.items():
        iris_sorted = sorted(iris)
        n = len(iris_sorted)
        if n:
            log.info("Enrichment: %s (%d items)…", kind, n)
        step = max(1, max(50, n // 20))  # every 50 or ~5%

        # Process in batches to reduce SPARQL round-trips dramatically
        batch_size = 200
        for i0, batch in enumerate(_chunk(iris_sorted, batch_size), start=0):
            labels_map = _labels_for_many(graph, backend, batch, cfg.lang_prefs)
            deprec_map = _deprecated_many(graph, backend, batch)
            ann_map = _annotations_for_many(graph, backend, batch, cfg.lang_prefs)

            for j, iri in enumerate(batch, start=1):
                labels = labels_map.get(iri, {})
                preferred = None
                for pref in (
                    "http://www.w3.org/2000/01/rdf-schema#label",
                    "http://www.w3.org/2004/02/skos/core#prefLabel",
                ):
                    if pref in labels and labels[pref]:
                        preferred = labels[pref][0][0]
                        break
                deprec = deprec_map.get(iri, False)
                annotations = ann_map.get(iri, {
                    "definition": None,
                    "comment": None,
                    "identifier": None,
                    "examples": [],
                    "scope_notes": [],
                })
                manch_lines: List[str] = []
                if getattr(cfg, "manchester_comments", True):
                    try:
                        if hasattr(m, "configure_label_lang_prefs"):
                            m.configure_label_lang_prefs(cfg.lang_prefs)
                        if kind == K_CLASS:
                            manch_lines = m.render_class_axioms(graph, iri)
                        elif kind == K_OBJECT_PROPERTY:
                            manch_lines = m.render_object_property_axioms(graph, iri)
                        elif kind == K_DATA_PROPERTY:
                            manch_lines = m.render_data_property_axioms(graph, iri)
                        elif kind == K_INDIVIDUAL:
                            manch_lines = m.render_individual_axioms(graph, iri)
                    except Exception:
                        manch_lines = []
                if manch_lines and cfg.max_axioms_per_entity:
                    manch_lines = manch_lines[: cfg.max_axioms_per_entity]
                enriched[kind][iri] = {
                    "iri": iri,
                    "labels": labels,
                    "preferred_label": preferred,
                    "deprecated": deprec,
                    "annotations": annotations,
                    "manchester": manch_lines,
                }
                processed += 1
                # progress log approximate per original cadence
                global_index = i0 * batch_size + j
                if global_index % step == 0 or global_index == n:
                    log.debug(
                        "Enrichment: %s %d/%d (%.0f%%), total %d/%d",
                        kind,
                        global_index,
                        n,
                        (global_index / max(1, n)) * 100,
                        processed,
                        total,
                    )
    return enriched
