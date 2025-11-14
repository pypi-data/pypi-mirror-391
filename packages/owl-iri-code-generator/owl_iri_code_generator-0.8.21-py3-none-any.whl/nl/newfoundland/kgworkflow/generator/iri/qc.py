import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List, Tuple, Any

from nl.newfoundland.kgworkflow.generator.iri.graph_loader import GraphMeta


@dataclass
class QCSummary:
    """Aggregate quality-control metrics for a single run.

    Fields capturing discovery/generation counts, naming stability, namespace
    coverage metrics, and missed IRI diagnostics.
    """
    ontology_iri: str
    version_iri: str
    triple_count: int
    graph_hash: str
    counts_discovered: Dict[str, int]
    counts_generated: Dict[str, int]
    deprecations: int
    naming_persisted: int
    collisions: Dict[str, List[Tuple[str, str]]]
    total_generated: int
    missed: Dict[str, Dict[str, Any]]  # {kind: {count: int, samples: [iri, ...]}}
    namespace_iri_counts: Dict[str, Dict[str, int]]  # {ns: {distinct: int, occurrences: int}}
    coverage_vs_distinct: Dict[str, float]  # {ns: coverage ratio 0..1}
    missed_namespace: Dict[str, Dict[str, Any]]  # {ns: {count: int, samples: [iri, ...]}}


def _count_namespace_iris(graph, backend, namespace: str) -> Dict[str, int]:
    """Count distinct IRIs and total occurrences under the namespace in S/P/O.

    Returns a dict with keys:
    - distinct: number of distinct IRIs starting with the namespace
    - occurrences: total occurrences across subject, predicate, and object
    """
    ns = namespace
    q_distinct = f"""
    SELECT (COUNT(DISTINCT ?x) AS ?n) WHERE {{
      {{ ?s ?p ?o . BIND(?s AS ?x) FILTER(isIRI(?x) && STRSTARTS(STR(?x), "{ns}")) }}
      UNION
      {{ ?s ?p ?o . BIND(?p AS ?x) FILTER(STRSTARTS(STR(?x), "{ns}")) }}
      UNION
      {{ ?s ?p ?o . BIND(?o AS ?x) FILTER(isIRI(?x) && STRSTARTS(STR(?x), "{ns}")) }}
    }}
    """
    q_occurrences = f"""
    SELECT (COUNT(?x) AS ?n) WHERE {{
      {{ ?s ?p ?o . BIND(?s AS ?x) FILTER(isIRI(?x) && STRSTARTS(STR(?x), "{ns}")) }}
      UNION
      {{ ?s ?p ?o . BIND(?p AS ?x) FILTER(STRSTARTS(STR(?x), "{ns}")) }}
      UNION
      {{ ?s ?p ?o . BIND(?o AS ?x) FILTER(isIRI(?x) && STRSTARTS(STR(?x), "{ns}")) }}
    }}
    """
    def _num(q: str) -> int:
        try:
            for row in backend.query(graph, q):
                return int(row[0])
        except Exception:
            return 0
        return 0
    return {"distinct": _num(q_distinct), "occurrences": _num(q_occurrences)}


def _list_namespace_iris(graph, backend, namespace: str) -> List[str]:
    ns = namespace
    q = f"""
    SELECT DISTINCT ?x WHERE {{
      {{ ?s ?p ?o . BIND(?s AS ?x) FILTER(isIRI(?x) && STRSTARTS(STR(?x), "{ns}")) }}
      UNION
      {{ ?s ?p ?o . BIND(?p AS ?x) FILTER(STRSTARTS(STR(?x), "{ns}")) }}
      UNION
      {{ ?s ?p ?o . BIND(?o AS ?x) FILTER(isIRI(?x) && STRSTARTS(STR(?x), "{ns}")) }}
    }}
    """
    out: List[str] = []
    try:
        for row in backend.query(graph, q):
            if row and row[0] is not None:
                out.append(str(row[0]))
    except Exception:
        return []
    return sorted(set(out))


def build_qc(meta: GraphMeta, discovered, assigned, naming_diag, cfg, graph=None, backend=None) -> QCSummary:
    """Assemble QC metrics for the run and compute namespace coverage.

    When `graph` and `backend` are provided, also compute namespace distinct IRI
    counts, coverage ratio (generated/distinct), and a full list of missed IRIs
    under the configured single namespace.
    """
    counts_disc = {k: len(v) for k, v in discovered.items()}
    counts_gen = {k: len(v) for k, v in assigned.items()}
    deprec = sum(1 for k in assigned for _, v in assigned[k].items() if v.get("deprecated"))
    total_generated = sum(counts_gen.values())

    # Missed IRIs per kind: discovered but not generated
    missed: Dict[str, Dict[str, Any]] = {}
    for kind, iris in discovered.items():
        gen_set = set(assigned.get(kind, {}).keys())
        miss = sorted([iri for iri in iris if iri not in gen_set])
        if miss:
            missed[kind] = {"count": len(miss), "samples": miss[:20]}
        else:
            missed[kind] = {"count": 0, "samples": []}

    # Namespace IRI counts and coverage vs distinct, plus missed namespace IRIs
    ns_counts: Dict[str, Dict[str, int]] = {}
    coverage_vs_distinct: Dict[str, float] = {}
    missed_namespace: Dict[str, Dict[str, Any]] = {}
    if graph is not None and backend is not None:
        # All generated IRIs across kinds
        generated_iris = set()
        for k in assigned.keys():
            generated_iris.update(assigned.get(k, {}).keys())
        ns = cfg.namespace
        ns_counts[ns] = _count_namespace_iris(graph, backend, ns)
        ns_all = _list_namespace_iris(graph, backend, ns)
        distinct = ns_counts[ns].get("distinct", 0) or len(ns_all)
        # Determine which generated IRIs fall under this namespace
        gen_in_ns = {iri for iri in generated_iris if iri.startswith(ns)}
        covered = len(gen_in_ns)
        cov = (covered / distinct) if distinct else 0.0
        coverage_vs_distinct[ns] = cov
        missed_list = [iri for iri in ns_all if iri not in gen_in_ns]
        missed_namespace[ns] = {"count": len(missed_list), "samples": missed_list[:20], "all": missed_list}

    return QCSummary(
        ontology_iri=meta.ontology_iri or "",
        version_iri=meta.version_iri or "",
        triple_count=meta.triple_count,
        graph_hash=meta.content_hash,
        counts_discovered=counts_disc,
        counts_generated=counts_gen,
        deprecations=deprec,
        naming_persisted=naming_diag.get("persisted_count", 0),
        collisions=naming_diag.get("collisions", {}),
        total_generated=total_generated,
        missed=missed,
        namespace_iri_counts=ns_counts,
        coverage_vs_distinct=coverage_vs_distinct,
        missed_namespace=missed_namespace,
    )


def emit_qc(qc: QCSummary, cfg) -> None:
    mode = cfg.qc_report

    # Always emit missed-IRI artifact if we have the data
    if qc.missed_namespace:
        out_txt = Path(cfg.out_dir) / "missed_iris.txt"
        out_txt.parent.mkdir(parents=True, exist_ok=True)
        # Single-namespace run: write header and full list for the configured namespace
        lines_txt: List[str] = []
        for ns, info in qc.missed_namespace.items():
            lines_txt.append(f"# Missed IRIs for namespace: {ns}")
            lines_txt.append(f"# Total missed: {info.get('count', 0)}")
            for iri in info.get("all", []):
                lines_txt.append(iri)
            lines_txt.append("")
        out_txt.write_text("\n".join(lines_txt).rstrip() + "\n", encoding="utf-8")

    if mode in ("stdout", "all"):
        print("QC Summary:")
        print(f"- Ontology IRI: {qc.ontology_iri}")
        print(f"- Version IRI: {qc.version_iri}")
        print(f"- Triples: {qc.triple_count}")
        print(f"- Graph hash: {qc.graph_hash}")
        print("- Discovered:", qc.counts_discovered)
        print("- Generated:", qc.counts_generated)
        print(f"- Total generated symbols: {qc.total_generated}")
        if qc.namespace_iri_counts:
            print("- Namespace IRI counts (distinct used for coverage):")
            for ns, nums in qc.namespace_iri_counts.items():
                distinct = nums.get('distinct', 0)
                cov = qc.coverage_vs_distinct.get(ns, 0.0)
                covered = int(round(distinct * cov)) if distinct else 0
                print(f"  - {ns}: distinct={distinct} | coverage={covered}/{distinct} ({cov*100:.1f}%)")
        if qc.missed_namespace:
            print("- Missed IRIs vs namespace distinct (not generated):")
            for ns, info in qc.missed_namespace.items():
                cnt = info.get("count", 0)
                samples = ", ".join(info.get("samples", []))
                if cnt > 0:
                    print(f"  - {ns}: {cnt} (samples: {samples})")
            print(f"  - Full list written to: {Path(cfg.out_dir) / 'missed_iris.txt'}")
        if qc.missed:
            print("- Missed IRIs (discovered but not generated):")
            for k, info in qc.missed.items():
                if info.get("count", 0) > 0:
                    print(f"  - {k}: {info['count']} (samples: {', '.join(info['samples'])})")
        print(f"- Deprecations: {qc.deprecations}")
        print(f"- Persisted names: {qc.naming_persisted}")
        print(f"- Collisions: {qc.collisions}")

    if mode in ("json", "all"):
        out = Path(cfg.out_dir) / "qc.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        with out.open("w", encoding="utf-8") as f:
            json.dump(asdict(qc), f, indent=2, ensure_ascii=False, sort_keys=True)

    if mode in ("md", "all"):
        out = Path(cfg.out_dir) / "qc.md"
        out.parent.mkdir(parents=True, exist_ok=True)
        lines = [
            "# QC Summary",
            f"- Ontology IRI: `{qc.ontology_iri}`",
            f"- Version IRI: `{qc.version_iri}`",
            f"- Triples: `{qc.triple_count}`",
            f"- Graph hash: `{qc.graph_hash}`",
            "- Discovered:", str(qc.counts_discovered),
            "- Generated:", str(qc.counts_generated),
            f"- Total generated symbols: `{qc.total_generated}`",
        ]
        if qc.namespace_iri_counts:
            lines.append("- Namespace IRI counts (distinct used for coverage):")
            for ns, nums in qc.namespace_iri_counts.items():
                distinct = nums.get('distinct', 0)
                cov = qc.coverage_vs_distinct.get(ns, 0.0)
                covered = int(round(distinct * cov)) if distinct else 0
                lines.append(f"  - `{ns}`: distinct=`{distinct}` | coverage=`{covered}/{distinct}` ({cov*100:.1f}%)")
        if qc.missed_namespace:
            lines.append("- Missed IRIs vs namespace distinct (not generated):")
            for ns, info in qc.missed_namespace.items():
                cnt = info.get("count", 0)
                if cnt > 0:
                    lines.append(f"  - `{ns}`: `{cnt}` (samples: {', '.join(info.get('samples', []))})")
            lines.append(f"  - Full list written to: `{(Path(cfg.out_dir) / 'missed_iris.txt')}`")
        if qc.missed:
            lines.append("- Missed IRIs (discovered but not generated):")
            for k, info in qc.missed.items():
                if info.get("count", 0) > 0:
                    lines.append(f"  - `{k}`: `{info['count']}` (samples: {', '.join(info['samples'])})")
        lines.extend([
            f"- Deprecations: `{qc.deprecations}`",
            f"- Persisted names: `{qc.naming_persisted}`",
            f"- Collisions: `{qc.collisions}`",
        ])
        out.write_text("\n".join(lines) + "\n", encoding="utf-8")
