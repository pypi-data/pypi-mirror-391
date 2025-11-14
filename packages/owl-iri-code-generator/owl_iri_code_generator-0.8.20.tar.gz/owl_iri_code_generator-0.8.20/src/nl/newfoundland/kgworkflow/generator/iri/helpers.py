from rdflib import URIRef


def as_uri(iri: str) -> URIRef:
    """Return a URIRef for the given IRI string.

    Convenience helper for consumers of the generated code.
    """
    return URIRef(iri)


def curie(prefix: str, local: str, sep: str = ":") -> str:
    """Return a simple CURIE string.

    This does not validate prefix maps; it's a lightweight formatting helper.
    """
    return f"{prefix}{sep}{local}"
