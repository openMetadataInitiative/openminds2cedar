# openminds2cedar

[![Tests](https://github.com/openMetadataInitiative/openminds2cedar/actions/workflows/tests.yml/badge.svg)](https://github.com/openMetadataInitiative/openminds2cedar/actions/workflows/tests.yml)

Generate CEDAR template elements from openMINDS schemas and convert filled instances back to openMINDS-LD.

> [!WARNING]
> **Pre-alpha (v0.0.1).** This is an early prototype. Generated elements, templates and output formats, as well as the CLI and Python API, may change. See [Known Limitations](#known-limitations).

## Quick Start

```bash
uv sync
cp .env.example .env  # Edit with your CEDAR API key
```

## CLI Commands

```bash
# Developer: generate elements and templates
uv run openminds2cedar generate core.Subject
uv run openminds2cedar template -r subject-study   # From registry definition
uv run openminds2cedar validate output/

# Publish when ready
uv run openminds2cedar publish output/elements/
uv run openminds2cedar publish output/templates/

# Curator: convert by instance ID
uv run openminds2cedar convert https://repo.metadatacenter.org/template-instances/xxx

# Utilities
uv run openminds2cedar sync     # Sync all CEDAR resources locally
```

## Workflows

### Developer Workflow

Generate CEDAR elements and templates, validate, and publish:

```bash
# 1. Generate elements and templates from registry
uv run openminds2cedar generate core.Subject
uv run openminds2cedar generate core.SubjectState
uv run openminds2cedar template -r subject-study  # Uses registry/templates.yaml

# 2. Validate via CEDAR API
uv run openminds2cedar validate output/

# 3. Publish to CEDAR
uv run openminds2cedar publish output/elements/
uv run openminds2cedar publish output/templates/
```

### Curator Workflow

Convert CEDAR instances to openMINDS:

```bash
# Convert by CEDAR instance ID (fetches from CEDAR)
uv run openminds2cedar convert https://repo.metadatacenter.org/template-instances/xxx

# Or convert local file
uv run openminds2cedar convert path/to/instance.json
```

The template ID is embedded in the instance (`schema:isBasedOn`), so only the instance ID is needed.

## Folder Structure

```
output/                         # All generated output (gitignored)
├── elements/                   # Generated CEDAR elements
│   └── core/
├── templates/                  # Generated CEDAR templates
└── openminds/                  # Converted openMINDS collections

src/openminds2cedar/
├── api/            # CEDAR Workbench API client
├── converters/     # CEDAR -> openMINDS conversion
├── generators/     # CEDAR element/template generation
└── registry/       # Schema and field configuration (YAML)
```

## Python API

```python
from openminds2cedar.generators import CEDARElementGenerator
from openminds2cedar.converters import CEDARToOpenMINDSConverter
from openminds2cedar.api import CEDARClient

# Generate element
gen = CEDARElementGenerator()
element = gen.generate("core.Subject")

# Upload to CEDAR
client = CEDARClient()
client.upload(element)

# Convert instance to openMINDS (by ID)
instance = client.get_instance("https://repo.metadatacenter.org/template-instances/xxx")
converter = CEDARToOpenMINDSConverter()
collection = converter.convert_instance(instance)
collection.save("output/openminds/")
```

## Configuration

Copy `.env.example` to `.env` and set:

```bash
CEDAR_API_KEY=your-api-key
CEDAR_FOLDER_ELEMENTS=https://repo.metadatacenter.org/folders/your-folder-id
CEDAR_FOLDER_TEMPLATES=https://repo.metadatacenter.org/folders/your-folder-id
CEDAR_FOLDER_INSTANCES=https://repo.metadatacenter.org/folders/your-folder-id
```

### Development vs Production

For development/testing, use a test folder on CEDAR. When ready for production:

1. Create production folders on CEDAR Workbench
2. Update `.env` with production folder IDs
3. Publish elements and templates to production folders

You can also specify the folder directly via CLI:
```bash
# Publish to specific folder
uv run openminds2cedar publish output/elements/ --folder https://repo.metadatacenter.org/folders/production-id
```

Registry files (schema/field/template config):
- `registry/schemas.yaml` - Which openMINDS schemas to generate
- `registry/fields.yaml` - Field mappings and controlled term classes
- `registry/templates.yaml` - Template definitions with cardinality

## Testing

```bash
uv run pytest
```

Tests marked `cedar` validate against the live CEDAR API and are skipped when `CEDAR_API_KEY` is not set. CI runs them using repository secrets.

## Known Limitations

- Only the schemas and fields configured in `registry/` are supported.
- Quantitative values (e.g. `weight`) are generated as plain numeric fields, so units are not captured.
- Instance generation (`CEDARInstanceGenerator`) currently supports the `subject-study` template only.
- `scripts/publish_test_resources.py` clears the configured CEDAR folders before uploading. Only point it at test folders.

## Status

Pre-alpha (v0.0.1). This project is in early development and has not been fully validated. Interfaces and output formats may change.

## Citation

If you use this software, please cite it using the metadata in [CITATION.cff](CITATION.cff).

## License

This project is licensed under [MIT](LICENSE).
