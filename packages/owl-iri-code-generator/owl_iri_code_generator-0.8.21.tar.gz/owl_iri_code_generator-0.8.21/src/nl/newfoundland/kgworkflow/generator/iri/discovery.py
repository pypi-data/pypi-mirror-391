"""Entity discovery across OWL kinds within a single namespace.

This module issues SPARQL queries to find IRIs for classes, properties, and
individuals that start with the configured namespace base IRI.
"""
from typing import Dict, Set

K_CLASS = "classes"
K_OBJECT_PROPERTY = "object_properties"
K_DATA_PROPERTY = "data_properties"
K_INDIVIDUAL = "individuals"
K_ANNOTATION_PROPERTY = "annotation_properties"

ALL_KINDS = [
    K_CLASS,
    K_OBJECT_PROPERTY,
    K_DATA_PROPERTY,
    K_INDIVIDUAL,
    K_ANNOTATION_PROPERTY,
]


def _values_block(namespace: str) -> str:
    """Return a single-variable VALUES block for the configured base IRI.

    rdflib and Oxigraph both accept: `VALUES ?base { <iri> }` for binding one value.
    """
    return f"VALUES ?base {{ <{namespace}> }}\n"


def _in_namespace_filter() -> str:
    """SPARQL filter that keeps IRIs starting with the bound ?base string."""
    return "FILTER(STRSTARTS(STR(?s), STR(?base)))\n"


def discover_entities(graph, cfg, backend) -> Dict[str, Set[str]]:
    """Discover entities per kind inside the single configured namespace.

    Returns a dict of kind -> set(iri).
    """
    ns_block = _values_block(cfg.namespace)
    ns_filter = _in_namespace_filter() if cfg.namespace else ""

    q_classes = f"""
    SELECT DISTINCT ?s WHERE {{
      {ns_block}
      ?s a owl:Class .
      {ns_filter}
      FILTER(?s != owl:Thing && ?s != owl:Nothing)
    }}
    """

    q_obj_props = f"""
    SELECT DISTINCT ?s WHERE {{
      {ns_block}
      ?s a owl:ObjectProperty .
      {ns_filter}
    }}
    """

    q_data_props = f"""
    SELECT DISTINCT ?s WHERE {{
      {ns_block}
      ?s a owl:DatatypeProperty .
      {ns_filter}
    }}
    """

    q_ann_props = f"""
    SELECT DISTINCT ?s WHERE {{
      {ns_block}
      ?s a owl:AnnotationProperty .
      {ns_filter}
    }}
    """

    # Individuals: typed resources excluding schema kinds
    q_inds = f"""
    SELECT DISTINCT ?s WHERE {{
      {ns_block}
      ?s a ?t .
      {ns_filter}

      # Keep existing exclusions (schema classes and the three main property classes)
      FILTER(?t NOT IN (
        owl:Class, rdfs:Class,
        owl:ObjectProperty, owl:DatatypeProperty, owl:AnnotationProperty
      ))

      # Ensure the resource is not declared to be any kind of property
      FILTER NOT EXISTS {{
        ?s a ?ptype .
        FILTER(?ptype IN (
          rdf:Property,
          owl:ObjectProperty, owl:DatatypeProperty, owl:AnnotationProperty,
          owl:FunctionalProperty, owl:InverseFunctionalProperty,
          owl:TransitiveProperty, owl:SymmetricProperty, owl:AsymmetricProperty,
          owl:ReflexiveProperty, owl:IrreflexiveProperty
        ))
      }}
    }}
    """

    prefix = """
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    """

    def run(q: str) -> Set[str]:
        """Execute the given SELECT and return the set of subject IRIs as strings."""
        rows = backend.query(graph, prefix + q)
        out = set()
        for row in rows:
            s = row[0]
            out.add(str(s))
        return out

    result = {
        K_CLASS: run(q_classes),
        K_OBJECT_PROPERTY: run(q_obj_props),
        K_DATA_PROPERTY: run(q_data_props),
        K_INDIVIDUAL: run(q_inds),
        K_ANNOTATION_PROPERTY: run(q_ann_props) if cfg.emit_annotation_properties else set(),
    }
    return result
