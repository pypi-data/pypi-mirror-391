# OWL IRI → Python Code Generator

The function of the tool is to generate deterministic Python modules that expose OWL ontology IRIs as `rdflib.URIRef` symbols, with rich Manchester-style axiomatization and annotations embedded as comments. This way it is easy to refer to ontology terms in Python code without having to worry about mapping IRIs.

An example of a generated class wrapper is:
```python
####################################################################################
# kind: Class
# label: continuant
# dc11:identifier: 008-BFO
# skos:definition: (Elucidation) A continuant is an entity that persists, endures,
#   or continues to exist through time while maintaining its identity (@en)
# skos:example: A human being; a tennis ball; a cave; a region of space; someone's
#   temperature (@en)
#
# SubClassOf: 'continuant part of' only 'continuant'
# SubClassOf: 'entity'
# DisjointWith: 'occurrent'
Continuant: Final[ClassIRI] = URIRef("http://purl.obolibrary.org/obo/BFO_0000002")
```

The tool includes a QC report, coverage diagnostics, and a persistent symbol map to keep names stable across runs if needed. 

The symbol map can be used to fine-tune the generated code for labels like "GMT-8", or for collisions; collisions are resolved automatically. The map overrides symbol generation during code generation. The map can also be used to keep the symbol mapping stable during the evolution of an ontology, or the tool itself. Note that refactoring the code is also a possibility, but the map is a more reliable way to keep the changes across runs. 

The symbol map format is a flat JSON object mapping IRI strings to identifiers, e.g.:
  ```json
  {
    "http://example.org/onto#MyClass": "MyClass",
    "http://example.org/onto#hasPart": "hasPart_op"
  }
  ```
## TL;DR
Optionally, look at the "Installing uv" in the next section and then install the tool:
```bash
uv tool install owl-iri-code-generator
```
You can now run the tool anywhere:
```bash
owl-iri-code-generator \
--ont bfo-core.ttl \
--namespace http://purl.obolibrary.org/obo/ \
--out-file BFO.py \
--qc-report stdout \
```

Look in tests/resources/ttl for some example ontologies.
### Installing uv
If uv isn’t installed yet, see https://docs.astral.sh/uv/ for platform‑specific instructions. Typical installation commands:
- macOS/Linux:
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```
- Windows (PowerShell):
  ```powershell
  iwr https://astral.sh/uv/install.ps1 -UseBasicParsing | iex
  ```
  
## Command-line interface
Run the generator:
```bash
owl-iri-code-generator \
  --ont PATH/TO/ontology.ttl \
  --namespace http://example.org/ontology/ \
  [options]
```

Options:
- `--ont PATH` (required): Path to the ontology file (any RDF format supported by rdflib).
- `--namespace IRI` (required): Base IRI to include (single namespace).
- `--lang CODE` (repeatable; default: `en`): Preferred label languages in priority order; can be repeated.
- `--symbol-style {snake|camel|custom}` (default: `custom`): Python identifier style.
  - `custom` is based on camelCase, but with two tweaks:
    - Class symbols start with a capital letter (UpperCamelCase).
    - Individual symbols are ensured to end with a trailing underscore (an underscore is appended if not present).
- `--out-dir PATH` (default: `out`): Output directory for generated files and QC artifacts.
- `--out-file NAME.py` (optional): Explicit output file name (e.g., `bfo.py`). 
- `--qc-report {stdout|md|json|all}` (default: `stdout`): QC output modes. `all` writes both `qc.md` and `qc.json` in `out/` and prints a console summary.
- `--unsupported-axiom-policy {warn|omit|raw}` (default: `warn`): How to handle unsupported OWL patterns in Manchester rendering.
- `--symbol-map PATH` (default: `symbol_map.json`): Path to persistent symbol-map JSON.
  - By default the symbol map is written under `out/` as `symbol_map.json`.
- `--dry-run` (flag): Generate QC and a preview JSON to stdout without writing files.
- `--log-level {DEBUG|INFO|WARNING|ERROR|CRITICAL}` (default: `INFO`): Controls verbosity of progress logging to stderr.

Notes:
- The generator does not follow `owl:imports`; provide a fully materialized ontology if needed.
- Progress logs are written to stderr; `--dry-run` preview JSON prints to stdout.
- The generated files are written under `out/` unless `--dry-run` is used.

### Generated code structure
- Top-of-file reproducibility header with source path, ontology IRI, version IRI, triple count, and graph hash and module-level constants.
- For each symbol, a comment block including:
  - Annotations: `label`, optional `alt` labels, `dc11:identifier`, definition/comment/examples/scope notes (full text, no truncation, including language tags).
  - Manchester axioms (e.g., `SubClassOf`, `EquivalentTo`, domains/ranges, property characteristics), unlimited by default.

## Quality Control (QC) output
The QC summary includes:
- Discovered vs. generated counts per kind.
- Total generated symbols and deprecation count.
- Naming stability stats (persisted names) and collision summaries.
- Namespace coverage vs. distinct IRIs within the provided namespace.
- Missed IRIs: per-kind (discovered but not generated) and per-namespace distinct lists, with the full list written to `out/missed_iris.txt`.

A typical run produces QC artifacts in `out/` (depending on `--qc-report`):
- Console summary (stdout) always when `stdout` or `all`.
- `out/qc.md` when `md` or `all`.
- `out/qc.json` when `json` or `all`.
- `out/missed_iris.txt`: complete list of namespace IRIs not covered by generation.

## Examples
Generate a BFO python file with full comments and QC to stdout:
```bash
owl-iri-code-generator \
--ont bfo-core.ttl \
--namespace http://purl.obolibrary.org/obo/ \
--out-file BFO.py \
--qc-report stdout 
```

Dry-run to preview without writing files:
```bash
owl-iri-code-generator \
--ont bfo-core.ttl \
--namespace http://purl.obolibrary.org/obo/ \
--out-file BFO.py \
--qc-report stdout \
--dry-run 
```

## One‑off execution with uv without installation
uv can resolve and install project dependencies on‑the‑fly for a single command. Nothing is written globally; uv uses a cache.
```bash
# Run the CLI directly using uv without installation
uv tool run owl-iri-code-generator \
--ont bfo-core.ttl \
--namespace http://purl.obolibrary.org/obo/ \
--out-file BFO.py \
--qc-report stdout
```
## Upgrading the tool with uv
If you installed the tool with `uv tool install`, you can upgrade it with:
or, if you want to upgrade:
```bash
uv tool upgrade owl-iri-code-generator
````
## Dependencies
From `pyproject.toml`:
- Python `>=3.11`
- `rdflib>=7.4.0` — RDF graph handling and SPARQL query engine
- `pyoxigraph>=0.5.2` — optional high-performance SPARQL backend
- `oxigraph>=0.5.2` — Oxigraph bindings/runtime (environment dependent)

Optional dev/test tools are not listed here; see `pyproject.toml`/`uv.lock` for details.
