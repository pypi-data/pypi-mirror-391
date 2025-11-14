"""
OWL to Python Code Generator

Generates Python modules exposing OWL entity IRIs as rdflib.URIRef constants, with
optional Manchester-style comments and QC reporting.

This package follows the project plan in Project_plan.md. It provides:
- CLI (see owl_to_python.cli:main)
- Backends for SPARQL (rdflib by default, optional Oxigraph)
- Discovery, enrichment, naming, rendering, and QC
- Persistent symbol map for name stability
"""

__all__ = [
    "cli",
    "helpers",
]
