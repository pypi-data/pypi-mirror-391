from typing import List, Optional, Tuple, Dict

from rdflib import URIRef

# Common IRIs used
RDF_TYPE = "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
RDF_FIRST = "http://www.w3.org/1999/02/22-rdf-syntax-ns#first"
RDF_REST = "http://www.w3.org/1999/02/22-rdf-syntax-ns#rest"
RDF_NIL = "http://www.w3.org/1999/02/22-rdf-syntax-ns#nil"

RDFS_SUBCLASS = "http://www.w3.org/2000/01/rdf-schema#subClassOf"
RDFS_SUBPROPERTY = "http://www.w3.org/2000/01/rdf-schema#subPropertyOf"
RDFS_DOMAIN = "http://www.w3.org/2000/01/rdf-schema#domain"
RDFS_RANGE = "http://www.w3.org/2000/01/rdf-schema#range"
RDFS_COMMENT = "http://www.w3.org/2000/01/rdf-schema#comment"

OWL_NS = "http://www.w3.org/2002/07/owl#"
OWL_CLASS = OWL_NS + "Class"
OWL_EQUIVALENT_CLASS = OWL_NS + "equivalentClass"
OWL_DISJOINT_WITH = OWL_NS + "disjointWith"
OWL_ALL_DISJOINT_CLASSES = OWL_NS + "AllDisjointClasses"
OWL_MEMBERS = OWL_NS + "members"

OWL_INTERSECTION_OF = OWL_NS + "intersectionOf"
OWL_UNION_OF = OWL_NS + "unionOf"
OWL_COMPLEMENT_OF = OWL_NS + "complementOf"

OWL_RESTRICTION = OWL_NS + "Restriction"
OWL_ON_PROPERTY = OWL_NS + "onProperty"
OWL_ON_CLASS = OWL_NS + "onClass"
OWL_SOME_VALUES_FROM = OWL_NS + "someValuesFrom"
OWL_ALL_VALUES_FROM = OWL_NS + "allValuesFrom"
OWL_HAS_VALUE = OWL_NS + "hasValue"
OWL_MIN_CARD = OWL_NS + "minCardinality"
OWL_MAX_CARD = OWL_NS + "maxCardinality"
OWL_EXACT_CARD = OWL_NS + "cardinality"
OWL_MIN_QUAL = OWL_NS + "minQualifiedCardinality"
OWL_MAX_QUAL = OWL_NS + "maxQualifiedCardinality"
OWL_EXACT_QUAL = OWL_NS + "qualifiedCardinality"
OWL_ON_DATA_RANGE = OWL_NS + "onDataRange"

OWL_INVERSE_OF = OWL_NS + "inverseOf"
OWL_PROPERTY_CHAIN_AXIOM = OWL_NS + "propertyChainAxiom"

# Characteristics
OWL_FUNC = OWL_NS + "FunctionalProperty"
OWL_INV_FUNC = OWL_NS + "InverseFunctionalProperty"
OWL_TRANS = OWL_NS + "TransitiveProperty"
OWL_SYMM = OWL_NS + "SymmetricProperty"
OWL_ASYMM = OWL_NS + "AsymmetricProperty"
OWL_REFL = OWL_NS + "ReflexiveProperty"
OWL_IRREFL = OWL_NS + "IrreflexiveProperty"


def _local(iri: str) -> str:
    if "#" in iri:
        return iri.rsplit("#", 1)[-1]
    return iri.rstrip("/").rsplit("/", 1)[-1]


# Label resolution and caching
_LABEL_CACHE: Dict[str, str] = {}
_LANG_PREFS: List[str] = ["en"]


def _render_iri(iri: str) -> str:
    # Fallback compact rendering when no graph/labels: use local name
    return _local(iri)


def configure_label_lang_prefs(langs: List[str]) -> None:
    global _LANG_PREFS
    _LANG_PREFS = list(langs) if langs else ["en"]


def _pick_best_label(values: List[Tuple[str, Optional[str]]]) -> Optional[str]:
    if not values:
        return None
    # sort by language preference order then lexicographically
    pref_index = {lang: i for i, lang in enumerate(_LANG_PREFS)}
    values_sorted = sorted(values, key=lambda t: (pref_index.get(t[1] or "", 999), t[0]))
    return values_sorted[0][0]


def _label_for(graph, iri: str) -> Optional[str]:
    # cache
    if iri in _LABEL_CACHE:
        return _LABEL_CACHE[iri]
    try:
        from rdflib import URIRef
    except Exception:  # pragma: no cover
        URIRef = None  # type: ignore
    labels: List[Tuple[str, Optional[str]]] = []
    s = URIRef(iri) if URIRef is not None else None
    if s is not None:
        # rdfs:label and skos:prefLabel
        for _, _, lit in graph.triples((s, URIRef("http://www.w3.org/2000/01/rdf-schema#label"), None)):
            val = str(lit)
            lang = getattr(lit, "language", None)
            labels.append((val, lang))
        for _, _, lit in graph.triples((s, URIRef("http://www.w3.org/2004/02/skos/core#prefLabel"), None)):
            val = str(lit)
            lang = getattr(lit, "language", None)
            labels.append((val, lang))
    best = _pick_best_label(labels)
    if best:
        _LABEL_CACHE[iri] = best
        return best
    return None


def _quote_label_for_manchester(text: str) -> str:
    """Wrap a label in single quotes for Manchester syntax, escaping as needed.

    - Escape backslashes first, then single quotes using backslash.
    - Collapse any newlines/tabs into spaces to keep one-line rendering.
    """
    if text is None:
        return "''"
    s = str(text).replace("\\", "\\\\").replace("'", "\\'")
    # Normalize control whitespace for readability in single-line comments
    s = s.replace("\n", " ").replace("\r", " ").replace("\t", " ")
    return f"'{s}'"


def _render_name(graph, iri: str) -> str:
    # Prefer label, fallback to local fragment
    lab = _label_for(graph, iri)
    return _quote_label_for_manchester(lab) if lab else _local(iri)


def _collect_list(graph, head) -> List:
    items = []
    cur = head
    # head can be a BNode or URIRef; iterate rdf:first/rest until rdf:nil
    visited = set()
    while cur and str(cur) != RDF_NIL:
        if str(cur) in visited:
            break
        visited.add(str(cur))
        first = None
        for _, _, f in graph.triples((cur, URIRef(RDF_FIRST), None)):
            first = f
            break
        if first is not None:
            items.append(first)
        nxt = None
        for _, _, r in graph.triples((cur, URIRef(RDF_REST), None)):
            nxt = r
            break
        if nxt is None:
            break
        cur = nxt
    return items


def _needs_parens(txt: str) -> bool:
    t = txt.strip()
    if (t.startswith("(") and t.endswith(")")) or t == "Thing" or t == "Nothing":
        return False
    for kw in [" and ", " or ", " not ", " some ", " only ", " value ", " min ", " max ", " exactly "]:
        if kw.strip() in t and kw in f" {t} ":
            return True
    # also if contains a space (labels with spaces) in composite contexts we'll add explicitly
    return False


def _parens(txt: str) -> str:
    return f"({txt})"


def _render_class_expr(graph, node) -> str:
    # Named class
    if isinstance(node, URIRef):
        return _render_name(graph, str(node))

    # BNode cases
    # Check restriction
    for _, _, t in graph.triples((node, URIRef(RDF_TYPE), None)):
        if str(t) == OWL_RESTRICTION:
            return _render_restriction(graph, node)

    # Boolean class constructors
    for _, _, lst in graph.triples((node, URIRef(OWL_INTERSECTION_OF), None)):
        parts = []
        for i in _collect_list(graph, lst):
            txt = _render_class_expr(graph, i)
            parts.append(_parens(txt) if _needs_parens(txt) else txt)
        return " and ".join(parts)
    for _, _, lst in graph.triples((node, URIRef(OWL_UNION_OF), None)):
        parts = []
        for i in _collect_list(graph, lst):
            txt = _render_class_expr(graph, i)
            parts.append(_parens(txt) if _needs_parens(txt) else txt)
        return " or ".join(parts)
    for _, _, c in graph.triples((node, URIRef(OWL_COMPLEMENT_OF), None)):
        inner = _render_class_expr(graph, c)
        return f"not {_parens(inner) if _needs_parens(inner) or ' ' in inner else inner}"

    # Fallback raw rendering
    return _render_iri(str(node))


def _render_value(graph, v) -> str:
    try:
        from rdflib.term import Literal
    except Exception:  # pragma: no cover
        Literal = None  # type: ignore
    if Literal is not None and isinstance(v, Literal):
        # Render with quotes and possibly datatype/lang
        sval = str(v)
        if v.language:
            return f'"{sval}"@{v.language}'
        if v.datatype:
            return f'"{sval}"^^{_render_iri(str(v.datatype))}'
        return f'"{sval}"'
    if isinstance(v, URIRef):
        return _render_name(graph, str(v))
    return _render_iri(str(v))


def _render_restriction(graph, node) -> str:
    prop = None
    for _, _, p in graph.triples((node, URIRef(OWL_ON_PROPERTY), None)):
        prop = p
        break
    ptxt = _render_name(graph, str(prop)) if prop is not None else "?P"

    # Qualified vs unqualified
    some = next(graph.triples((node, URIRef(OWL_SOME_VALUES_FROM), None)), None)
    if some:
        _, _, filler = some
        ftxt = _render_class_expr(graph, filler)
        ftxt = _parens(ftxt) if _needs_parens(ftxt) or " " in ftxt else ftxt
        return f"{ptxt} some {ftxt}"
    allv = next(graph.triples((node, URIRef(OWL_ALL_VALUES_FROM), None)), None)
    if allv:
        _, _, filler = allv
        ftxt = _render_class_expr(graph, filler)
        ftxt = _parens(ftxt) if _needs_parens(ftxt) or " " in ftxt else ftxt
        return f"{ptxt} only {ftxt}"
    hv = next(graph.triples((node, URIRef(OWL_HAS_VALUE), None)), None)
    if hv:
        _, _, val = hv
        return f"{ptxt} value {_render_value(graph, val)}"

    # Cardinalities
    card = next(graph.triples((node, URIRef(OWL_MIN_CARD), None)), None)
    if card:
        _, _, lit = card
        return f"{ptxt} min {str(lit)}"
    card = next(graph.triples((node, URIRef(OWL_MAX_CARD), None)), None)
    if card:
        _, _, lit = card
        return f"{ptxt} max {str(lit)}"
    card = next(graph.triples((node, URIRef(OWL_EXACT_CARD), None)), None)
    if card:
        _, _, lit = card
        return f"{ptxt} exactly {str(lit)}"

    # Qualified cardinalities
    for pred, word in (
            (OWL_MIN_QUAL, "min"),
            (OWL_MAX_QUAL, "max"),
            (OWL_EXACT_QUAL, "exactly"),
    ):
        t = next(graph.triples((node, URIRef(pred), None)), None)
        if t:
            _, _, n = t
            # Try onClass or onDataRange for filler
            filler_node = None
            oc = next(graph.triples((node, URIRef(OWL_ON_CLASS), None)), None)
            if oc:
                _, _, filler_node = oc
            else:
                od = next(graph.triples((node, URIRef(OWL_ON_DATA_RANGE), None)), None)
                if od:
                    _, _, filler_node = od
            if filler_node is not None:
                ftxt = _render_class_expr(graph, filler_node)
                ftxt = _parens(ftxt) if _needs_parens(ftxt) or " " in ftxt else ftxt
                return f"{ptxt} {word} {str(n)} {ftxt}"
            return f"{ptxt} {word} {str(n)}"

    return f"{ptxt} some Thing"  # conservative fallback


def _render_property_expr(graph, node) -> str:
    # Named
    if isinstance(node, URIRef):
        return _render_name(graph, str(node))
    # inverseOf
    inv = next(graph.triples((node, URIRef(OWL_INVERSE_OF), None)), None)
    if inv:
        _, _, p = inv
        return f"inverse {_render_property_expr(graph, p)}"
    return _render_iri(str(node))


# High-level collectors per entity kind

def render_class_axioms(graph, iri: str) -> List[str]:
    s = URIRef(iri)
    lines: List[str] = []

    # SubClassOf
    subs = []
    for _, _, o in graph.triples((s, URIRef(RDFS_SUBCLASS), None)):
        subs.append(o)
    for o in subs:
        lines.append(f"SubClassOf: {_render_class_expr(graph, o)}")

    # EquivalentTo
    for _, _, o in graph.triples((s, URIRef(OWL_EQUIVALENT_CLASS), None)):
        lines.append(f"EquivalentTo: {_render_class_expr(graph, o)}")

    # DisjointWith
    for _, _, o in graph.triples((s, URIRef(OWL_DISJOINT_WITH), None)):
        lines.append(f"DisjointWith: {_render_class_expr(graph, o)}")

    # AllDisjointClasses memberships
    # Find groups where s is a member
    for g, _, members_list in graph.triples((None, URIRef(OWL_MEMBERS), None)):
        is_group = any(1 for _ in graph.triples((g, URIRef(RDF_TYPE), URIRef(OWL_ALL_DISJOINT_CLASSES))))
        if not is_group:
            continue
        members = _collect_list(graph, members_list)
        member_iris = [m for m in members if isinstance(m, URIRef)]
        if s in member_iris:
            others = [m for m in member_iris if m != s]
            if others:
                rendered = ", ".join(_render_name(graph, str(x)) for x in others)
                lines.append(f"DisjointWith: {rendered}")

    return lines


def render_object_property_axioms(graph, iri: str) -> List[str]:
    p = URIRef(iri)
    lines: List[str] = []

    # SubPropertyOf
    for _, _, o in graph.triples((p, URIRef(RDFS_SUBPROPERTY), None)):
        lines.append(f"SubPropertyOf: {_render_property_expr(graph, o)}")

    # InverseOf
    for _, _, o in graph.triples((p, URIRef(OWL_INVERSE_OF), None)):
        lines.append(f"InverseOf: {_render_property_expr(graph, o)}")

    # Domain / Range (can be expressions)
    for _, _, d in graph.triples((p, URIRef(RDFS_DOMAIN), None)):
        dtxt = _render_class_expr(graph, d)
        dtxt = _parens(dtxt) if _needs_parens(dtxt) or " " in dtxt else dtxt
        lines.append(f"Domain: {dtxt}")
    for _, _, r in graph.triples((p, URIRef(RDFS_RANGE), None)):
        rtxt = _render_class_expr(graph, r)
        rtxt = _parens(rtxt) if _needs_parens(rtxt) or " " in rtxt else rtxt
        lines.append(f"Range: {rtxt}")

    # Property chain
    for _, _, chain in graph.triples((p, URIRef(OWL_PROPERTY_CHAIN_AXIOM), None)):
        parts = [_render_property_expr(graph, i) for i in _collect_list(graph, chain)]
        if parts:
            lines.append(f"PropertyChain: {' o '.join(parts)}")

    # Characteristics from rdf:type
    chars = []
    for _, _, t in graph.triples((p, URIRef(RDF_TYPE), None)):
        t = str(t)
        if t == OWL_TRANS:
            chars.append("transitive")
        elif t == OWL_SYMM:
            chars.append("symmetric")
        elif t == OWL_FUNC:
            chars.append("functional")
        elif t == OWL_INV_FUNC:
            chars.append("inverseFunctional")
        elif t == OWL_ASYMM:
            chars.append("asymmetric")
        elif t == OWL_REFL:
            chars.append("reflexive")
        elif t == OWL_IRREFL:
            chars.append("irreflexive")
    if chars:
        lines.append(f"Characteristics: {', '.join(sorted(chars))}")

    return lines


def render_data_property_axioms(graph, iri: str) -> List[str]:
    p = URIRef(iri)
    lines: List[str] = []
    # SubPropertyOf
    for _, _, o in graph.triples((p, URIRef(RDFS_SUBPROPERTY), None)):
        lines.append(f"SubPropertyOf: {_render_property_expr(graph, o)}")
    # Domain / Range (range typically datatype)
    for _, _, d in graph.triples((p, URIRef(RDFS_DOMAIN), None)):
        lines.append(f"Domain: {_render_class_expr(graph, d)}")
    for _, _, r in graph.triples((p, URIRef(RDFS_RANGE), None)):
        if isinstance(r, URIRef):
            lines.append(f"Range: {_render_iri(str(r))}")
        else:
            lines.append(f"Range: {_render_class_expr(graph, r)}")
    # Functional
    for _, _, t in graph.triples((p, URIRef(RDF_TYPE), None)):
        if str(t) == OWL_FUNC:
            lines.append("Characteristics: functional")
    return lines


def render_individual_axioms(graph, iri: str) -> List[str]:
    s = URIRef(iri)
    lines: List[str] = []
    # Types
    for _, _, t in graph.triples((s, URIRef(RDF_TYPE), None)):
        # skip schema/property kinds to avoid noise
        st = str(t)
        if st in (OWL_CLASS, OWL_FUNC, OWL_INV_FUNC, OWL_TRANS, OWL_SYMM, OWL_ASYMM, OWL_REFL, OWL_IRREFL):
            continue
        lines.append(f"Type: {_render_class_expr(graph, t)}")
    # Facts (object and data property assertions)
    for p, o in graph.predicate_objects(subject=s):
        ps = str(p)
        if ps in (RDF_TYPE,):
            continue
        # Skip annotation properties commonly used for metadata to avoid duplication with annotations section
        if ps in (
                "http://www.w3.org/2000/01/rdf-schema#label",
                "http://www.w3.org/2000/01/rdf-schema#comment",
                "http://www.w3.org/2004/02/skos/core#prefLabel",
                "http://www.w3.org/2004/02/skos/core#altLabel",
                "http://www.w3.org/2004/02/skos/core#definition",
                "http://www.w3.org/2004/02/skos/core#example",
                "http://www.w3.org/2004/02/skos/core#scopeNote",
                "http://purl.obolibrary.org/obo/IAO_0000115",
                "http://purl.org/dc/elements/1.1/identifier",
                "http://purl.org/dc/terms/identifier",
                "http://purl.org/dc/terms/description",
                "http://purl.org/dc/terms/title",
        ):
            continue
        # Also skip any predicate typed as owl:AnnotationProperty
        is_annotation = any(1 for _ in graph.triples((p, URIRef(OWL_NS + 'AnnotationProperty'), None)))
        if is_annotation:
            continue
        lines.append(f"Fact: {_render_property_expr(graph, p)} {_render_value(graph, o)}")
    # SameAs / DifferentFrom
    for _, _, o in graph.triples((s, URIRef(OWL_NS + 'sameAs'), None)):
        lines.append(f"SameAs: {_render_name(graph, str(o))}")
    for _, _, o in graph.triples((s, URIRef(OWL_NS + 'differentFrom'), None)):
        lines.append(f"DifferentFrom: {_render_name(graph, str(o))}")
    return lines
