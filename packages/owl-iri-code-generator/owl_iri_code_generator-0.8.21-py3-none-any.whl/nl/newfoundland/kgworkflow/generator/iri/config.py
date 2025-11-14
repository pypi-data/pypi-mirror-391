from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional


@dataclass
class Config:
    """Runtime configuration for a single generation run.

    Notes:
    - This tool operates on a single namespace (base IRI) per run. The `namespace`
      field contains that base IRI as a string.
    - Label language preferences are ordered most-to-least preferred.
    - The remaining fields control generation style, QC outputs, and backend.
    """

    ont_path: Path
    namespace: str  # Single namespace base IRI to include
    lang_prefs: List[str]
    symbol_style: str  # "snake" | "camel" | "custom"
    out_dir: Path
    qc_report: str  # "stdout" | "md" | "json" | "all"
    manchester_comments: bool
    max_axioms_per_entity: int
    unsupported_axiom_policy: str  # "warn" | "omit" | "raw"
    emit_annotation_properties: bool
    symbol_map: Path
    dry_run: bool
    backend: str  # "rdflib" | "oxigraph"
    out_file: Optional[str] = None  # Output file name, overrides default
