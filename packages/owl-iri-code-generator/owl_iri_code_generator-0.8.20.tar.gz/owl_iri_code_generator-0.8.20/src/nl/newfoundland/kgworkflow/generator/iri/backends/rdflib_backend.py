from typing import Optional

try:
    from rdflib import Graph
except Exception:  # pragma: no cover
    Graph = object  # type: ignore


class RdflibBackend:
    """Thin wrapper providing a SPARQL interface on an rdflib.Graph."""

    name = "rdflib"

    def query(self, graph: Graph, sparql: str, initBindings: Optional[dict] = None):
        """Execute the given SPARQL query against the rdflib graph and return rows.

        Returns an iterable where each row supports index-based access (tuple-like).
        """
        return graph.query(sparql, initBindings=initBindings or {})
