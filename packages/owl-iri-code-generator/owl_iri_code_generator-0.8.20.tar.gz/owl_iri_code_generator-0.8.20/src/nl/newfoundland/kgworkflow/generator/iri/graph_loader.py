from dataclasses import dataclass
from hashlib import sha256
from typing import Optional, Tuple

from rdflib import Graph, RDF, OWL
import importlib


@dataclass
class GraphMeta:
    ontology_iri: Optional[str]
    version_iri: Optional[str]
    triple_count: int
    content_hash: str
    source_path: str


def _make_graph(backend: str):
    """Create an rdflib Graph.

    Behavior:
    - If oxrdflib is available, prefer rdflib's "Oxigraph" store for better SPARQL performance,
      regardless of the configured backend (keeps CLI simple while benefiting from oxrdflib).
    - Otherwise, fall back to the default in-memory rdflib Graph.
    """
    try:
        has_oxrdflib = importlib.util.find_spec("oxrdflib") is not None
    except Exception:
        has_oxrdflib = False

    if has_oxrdflib:
        # oxrdflib registers an rdflib store named "Oxigraph"
        g = Graph(store="Oxigraph")
        try:
            # In-memory store; for persistence pass a directory path instead of None
            g.open(None, create=True)
        except Exception:
            # Some versions of rdflib/oxrdflib don't require open(); ignore
            pass
        return g

    return Graph()


def load_graph_and_metadata(cfg) -> Tuple["Graph", GraphMeta]:
    """Load the RDF graph from disk and compute basic reproducibility metadata."""
    g = _make_graph(cfg.backend)
    # Parse without following imports; rdflib doesn't follow imports by default.
    g.parse(str(cfg.ont_path))

    # Try to find ontology IRI and version IRI
    ont_iri = None
    version_iri = None
    try:
        for s in g.subjects(RDF.type, OWL.Ontology):  # type: ignore
            ont_iri = str(s)
            for vi in g.objects(s, OWL.versionIRI):  # type: ignore
                version_iri = str(vi)
            break
    except Exception:
        pass

    # Triple count
    triple_count = len(g)

    # Content hash: hash N-Triples serialization for determinism
    data = g.serialize(format="nt")  # type: ignore
    if isinstance(data, bytes):
        buf = data
    else:
        buf = data.encode("utf-8")
    content_hash = sha256(buf).hexdigest()

    meta = GraphMeta(
        ontology_iri=ont_iri,
        version_iri=version_iri,
        triple_count=triple_count,
        content_hash=content_hash,
        source_path=str(cfg.ont_path),
    )
    return g, meta
