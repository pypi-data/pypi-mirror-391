import argparse
import json
import sys
import logging
import time
from pathlib import Path
from typing import List, Optional

from nl.newfoundland.kgworkflow.generator.iri.backends.rdflib_backend import RdflibBackend
from nl.newfoundland.kgworkflow.generator.iri.config import Config
from nl.newfoundland.kgworkflow.generator.iri.discovery import discover_entities
from nl.newfoundland.kgworkflow.generator.iri.enrichment import enrich_entities
from nl.newfoundland.kgworkflow.generator.iri.graph_loader import load_graph_and_metadata
from nl.newfoundland.kgworkflow.generator.iri.naming import assign_names
from nl.newfoundland.kgworkflow.generator.iri.qc import build_qc, emit_qc
from nl.newfoundland.kgworkflow.generator.iri.rendering import render_output
from nl.newfoundland.kgworkflow.generator.iri.symbol_map import load_symbol_map, save_symbol_map


def build_arg_parser() -> argparse.ArgumentParser:
    """Build and return the CLI argument parser for the generator.

    Notes:
    - This tool operates on a single namespace per run; use --namespace to set it.
    - Progress logs go to stderr; JSON previews (when --dry-run) go to stdout.
    """
    p = argparse.ArgumentParser(description="OWL to Python code generator")
    # Support -? as a familiar alias for help, in addition to -h/--help
    p.add_argument("-?", action="help", help="Show this help message and exit")
    p.add_argument("--ont", required=True, help="Path to ontology file")
    p.add_argument("--namespace", required=True, help="Namespace base IRI to include (single namespace)")
    p.add_argument("--lang", action="append", default=["en"], help="Preferred label language(s); repeatable")
    #p.add_argument("--emit-style", choices=["class", "module"], default="class")
    #p.add_argument("--class-name", default=None,
    #               help="Wrapper class name for generated file when --emit-style=class (e.g., 'BFO')")
    #p.add_argument("--manchester-comments", choices=["true", "false"], default="true")
    #p.add_argument("--backend", choices=["rdflib", "oxigraph"], default="oxigraph", help="SPARQL backend")
    #p.add_argument("--max-axioms-per-entity", type=int, default=0, help="Maximum Manchester axioms per entity; 0 means unlimited")
    #p.add_argument("--emit-annotation-properties", choices=["true", "false"], default="true")
    p.add_argument("--symbol-style", choices=["snake", "camel", "custom"], default="custom")
    p.add_argument("--out-dir", default="out", help="Output directory for generated files")
    p.add_argument("--qc-report", choices=["stdout", "md", "json", "all"], default="stdout")
    p.add_argument("--unsupported-axiom-policy", choices=["warn", "omit", "raw"], default="warn")
    p.add_argument("--symbol-map", default="symbol_map.json", help="Path to persistent symbol map JSON file. By default, the file is written under --out-dir as 'symbol_map.json'. Pass an explicit path to override this location.")
    p.add_argument("--dry-run", action="store_true", help="Generate QC and preview without writing files")
    p.add_argument("--out-file", default="ontology.py",
                   help="Optional output file name (e.g., 'ontology.py').")
    p.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                   help="Logging level for progress reporting")
    return p


def main(argv: Optional[List[str]] = None) -> int:
    """Entry point for the CLI.

    Parses arguments, orchestrates the pipeline (load → discover → enrich → name →
    QC → render → save symbol map), and returns a process exit code.
    """
    args = build_arg_parser().parse_args(argv)

    # Configure logging
    level = getattr(logging, str(args.log_level).upper(), logging.INFO)
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        datefmt="%H:%M:%S",
        stream=sys.stderr,
    )
    log = logging.getLogger("OwlIriToCodeGenerator")

    # Determine symbol map path and default placement under out-dir
    # If --symbol-map is explicitly provided (not the default), honor it as-is.
    # Otherwise, place the default filename under --out-dir.
    symbol_map_is_default = (args.symbol_map == "symbol_map.json" or not args.symbol_map)
    if symbol_map_is_default:
        base_filename = "symbol_map.json"
        effective_symbol_map_path = Path(args.out_dir) / base_filename
        logging.getLogger("OwlIriToCodeGenerator").debug(
            "Using default symbol map path under out-dir: %s", effective_symbol_map_path
        )
    else:
        effective_symbol_map_path = Path(args.symbol_map)
        logging.getLogger("OwlIriToCodeGenerator").debug(
            "Using explicit --symbol-map path: %s", effective_symbol_map_path
        )

    cfg = Config(
        ont_path=Path(args.ont),
        namespace=args.namespace,
        lang_prefs=args.lang,
        symbol_style=args.symbol_style,
        out_dir=Path(args.out_dir),
        qc_report=args.qc_report,
        manchester_comments=True,
        max_axioms_per_entity=0,
        unsupported_axiom_policy=args.unsupported_axiom_policy,
        emit_annotation_properties=True,
        symbol_map=effective_symbol_map_path,
        dry_run=args.dry_run,
        backend="rdflib",
        out_file=args.out_file,
    )

    # Determine load path for legacy symbol maps: if using the default location and
    # the out-dir file does not exist yet, but a legacy root-level file exists with
    # the same base filename, load from the legacy file to preserve stability, but
    # still save to the new out-dir location.
    load_symbol_map_path = cfg.symbol_map
    if symbol_map_is_default:
        if not cfg.symbol_map.exists():
            legacy_candidate = Path(base_filename)
            if legacy_candidate.exists():
                logging.getLogger("OwlIriToCodeGenerator").info(
                    "Loading symbol map from legacy path %s (will be saved to %s)",
                    legacy_candidate,
                    cfg.symbol_map,
                )
                load_symbol_map_path = legacy_candidate

    # Backend selection (engine is chosen in graph_loader via cfg.backend)
    t0 = time.perf_counter()
    try:
        import importlib
        has_ox = importlib.util.find_spec("oxrdflib") is not None
    except Exception:
        has_ox = False
    if has_ox:
        log.info("Backend: rdflib (Oxigraph via oxrdflib)")
    else:
        log.info("Backend: rdflib")
    backend = RdflibBackend()

    # Load graph
    log.info("Loading graph and metadata from %s", cfg.ont_path)
    t = time.perf_counter()
    graph, meta = load_graph_and_metadata(cfg)
    log.info("Loaded graph: %s triples (%.2fs)", getattr(meta, "triple_count", "?"), time.perf_counter() - t)

    # Discover entities
    log.info("Discovering entities in namespace %s", cfg.namespace)
    t = time.perf_counter()
    discovered = discover_entities(graph, cfg, backend)
    disc_time = time.perf_counter() - t
    total_disc = sum(len(v) for v in discovered.values())
    log.info("Discovered %d entities (%.2fs)", total_disc, disc_time)

    # Enrich entities
    log.info("Enriching entities (labels, annotations, axioms)…")
    t = time.perf_counter()
    enriched = enrich_entities(graph, discovered, cfg, backend)
    enr_time = time.perf_counter() - t
    log.info("Enrichment complete (%.2fs)", enr_time)

    # Naming
    log.info("Assigning symbols…")
    t = time.perf_counter()
    symbol_map = load_symbol_map(load_symbol_map_path)
    assigned, symbol_map, naming_diag = assign_names(enriched, cfg, symbol_map)
    log.info("Assigned symbols for %d entities (%.2fs)", sum(len(v) for v in assigned.values()), time.perf_counter() - t)

    # QC
    log.info("Building QC report…")
    t = time.perf_counter()
    qc = build_qc(meta, discovered, assigned, naming_diag, cfg, graph=graph, backend=backend)
    emit_qc(qc, cfg)
    log.info("QC emitted (%.2fs)", time.perf_counter() - t)

    # Render
    if not cfg.dry_run:
        log.info("Rendering output to %s…", cfg.out_dir)
        t = time.perf_counter()
        render_output(assigned, meta, cfg)
        log.info("Render complete (%.2fs)", time.perf_counter() - t)

        log.info("Saving symbol map to %s", cfg.symbol_map)
        save_symbol_map(cfg.symbol_map, symbol_map)
    else:
        # In dry-run, print a small preview to stdout
        preview = {
            "preview_symbols": {k: list(v.keys()) for k, v in assigned.items()},
            "out_dir": str(cfg.out_dir),
        }
        print(json.dumps(preview, indent=2))

    log.info("Done in %.2fs", time.perf_counter() - t0)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
