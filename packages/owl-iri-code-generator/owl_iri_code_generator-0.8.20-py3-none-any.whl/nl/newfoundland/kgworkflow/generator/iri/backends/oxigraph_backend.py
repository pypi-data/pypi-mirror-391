import importlib
from typing import Iterable, List, Optional, Tuple

# We depend on rdflib Graph as input for now
from rdflib import BNode as RDFLibBNode
from rdflib import Graph as RDFLibGraph
from rdflib import Literal as RDFLibLiteral
from rdflib import URIRef as RDFLibURIRef


def is_oxigraph_available() -> bool:
    return importlib.util.find_spec("pyoxigraph") is not None


class OxigraphBackend:
    """Faster SPARQL backend using pyoxigraph.Store.

    This backend lazily builds a pyoxigraph Store from the provided rdflib.Graph on
    first use (or when the graph object changes), then executes all SPARQL queries
    against the in-memory Oxigraph store.
    """

    name = "oxigraph"

    def __init__(self):
        if not is_oxigraph_available():
            raise RuntimeError("Oxigraph not available")
        # Lazy import
        from pyoxigraph import Store  # type: ignore

        self._Store = Store
        self._store = None  # created on first use
        self._graph_id: Optional[int] = None

    # --- Internal helpers -----------------------------------------------------
    def _ensure_loaded(self, graph: RDFLibGraph) -> None:
        """Load rdflib.Graph triples into the Oxigraph Store if not already loaded."""
        gid = id(graph)
        if self._store is not None and self._graph_id == gid:
            return

        # (Re)build store
        self._store = self._Store()
        self._graph_id = gid

        # Lazy import pyoxigraph terms
        from pyoxigraph import BlankNode, Literal, NamedNode, Quad  # type: ignore

        def to_ox_term(t):
            if isinstance(t, RDFLibURIRef):
                return NamedNode(str(t))
            if isinstance(t, RDFLibBNode):
                # Keep rdflib BNode id
                return BlankNode(str(t))
            if isinstance(t, RDFLibLiteral):
                # rdflib literal → oxigraph Literal
                if t.datatype:
                    return Literal(str(t), datatype=NamedNode(str(t.datatype)))
                if t.language:
                    return Literal(str(t), language=str(t.language))
                return Literal(str(t))
            # Fallback to string representation
            return NamedNode(str(t)) if str(t).startswith("http") else Literal(str(t))

        # Load all triples as default graph quads
        add = self._store.add
        for s, p, o in graph.triples((None, None, None)):
            add(Quad(to_ox_term(s), to_ox_term(p), to_ox_term(o), None))

    def _run_select(self, sparql: str) -> Tuple[List[str], Iterable[Tuple[object, ...]]]:
        """Execute a SELECT and return (variables, row-tuples)."""
        from pyoxigraph import QuerySolutions, Variable  # type: ignore

        try:
            res = self._store.query(sparql)
        except Exception as e:
            # Re-raise with the SPARQL text to aid debugging
            raise RuntimeError(f"Oxigraph SPARQL error: {e}\nQuery was:\n{sparql}")
        if not isinstance(res, QuerySolutions):
            # For ASK/CONSTRUCT/DESCRIBE we return empty results; our code only uses SELECT
            return [], []
        # Build variable names without leading '?', and keep Variable objects for lookups
        def _var_name(v) -> str:
            try:
                name = v.name  # type: ignore[attr-defined]
                if isinstance(name, str):
                    return name
            except Exception:
                pass
            s = str(v)
            return s[1:] if s.startswith("?") else s
        var_objs = list(res.variables)
        vars_order = [_var_name(v) for v in var_objs]

        # Convert terms to simple Python values (strings/None) to match our usage
        def term_to_py(t):
            if t is None:
                return None
            tv = getattr(t, "value", None)
            if tv is not None:
                return str(tv)
            return str(t)

        rows: List[Tuple[object, ...]] = []
        for sol in res:
            # Use the Variable objects directly to avoid name/key mismatches
            vals = []
            for vobj in var_objs:
                try:
                    val = sol.value(vobj)  # type: ignore[attr-defined]
                except Exception:
                    # Fallbacks if value() is unavailable
                    try:
                        val = sol[vobj]  # type: ignore[index]
                    except Exception:
                        val = None
                vals.append(term_to_py(val))
            rows.append(tuple(vals))
        return vars_order, rows

    # --- Public API -----------------------------------------------------------
    def query(self, graph: RDFLibGraph, sparql: str, initBindings: Optional[dict] = None):
        """Execute a SPARQL SELECT against the internal Oxigraph store.

        Returns an iterable of tuples to mimic rdflib's row-like access by
        index. `initBindings` is ignored; inline bindings in the SPARQL when
        needed.
        """
        # initBindings is not supported by pyoxigraph directly for now; our queries
        # don't rely on it. If needed, we can inline bindings into the SPARQL.
        self._ensure_loaded(graph)
        _vars, rows = self._run_select(sparql)
        # Return an iterable of tuples to mimic rdflib's row-like access by index
        return rows
