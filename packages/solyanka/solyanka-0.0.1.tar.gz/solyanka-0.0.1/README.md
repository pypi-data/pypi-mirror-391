# Solyanka

Shared helpers and datasets that power the statement generators and downstream synthetic-data
pipelines (including LLM fine-tuning sets).
The first module exported by this repository focuses on transaction patterns: the curated YAML
files, the schema that keeps them in shape, and a tiny loader to consume them from any
application (FastAPI, CLI tools, notebooks, etc).

## Installation

```bash
pip install solyanka
```

For local development (tests + linters):

```bash
pip install -e ".[dev]"
```

## Usage

```python
from solyanka import PatternsService, EEA_COUNTRIES

service = PatternsService()
general = service.load_general_patterns()
eea = service.load_eea_patterns()
thailand_specific = service.load_country_patterns("Thailand")

# Preferred helper: auto-mix general + (eea) + country overrides
full_set = service.get_country_patterns("Germany")

# Advanced filtering (e.g. validation scripts)
custom = service.get_patterns(country="Germany", include="general,eea")

# API-friendly dicts
payload = service.get_pattern_dicts(country="Spain")
```

If you need to point the loader to different files (e.g. while editing YAML locally),
either pass `PatternsService(base_dir=Path("./transaction_patterns"))` or set the
`TRANSACTION_PATTERNS_DIR` environment variable.

## Pattern sets

- **General** – always included via `load_general_patterns()`.
- **EEA** – supplement auto-applied for EEA countries via `load_eea_patterns()`.
- **Country-specific** – call `load_country_patterns("Germany")`; the helper normalizes slugs internally.

`get_country_patterns(country)` mixes general + (EEA when applicable) + country-level patterns and accepts empty/None values.
`get_patterns(country, include)` exposes finer control when tooling needs only certain slices. `include` accepts a comma-separated subset of `{"general", "eea", "country"}`; invalid values raise `ValueError`.
`get_pattern_dicts(...)` mirrors these parameters but returns normalized dictionaries that are ready for JSON responses.

## Development

- `pytest` validates every YAML file against `schema.json`.
- GitHub Actions run tests on push/pull_request and build/publish artifacts when a semver tag is pushed.

Contributions should keep the dataset human-friendly: no generated UUIDs in the patterns,
clear field names, and comments that help reviewers understand why a pattern exists.

### Tests

```bash
poetry run pytest
```
