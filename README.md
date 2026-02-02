# openminds2cedar

Generate CEDAR template elements from openMINDS schemas and convert filled instances back to openMINDS-LD.

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

## Roadmap

- [x] **Generic converter**: Schema-driven conversion using `@context` types and property introspection
- [ ] **Declarative UI**: Configure field UI (inputType, help text) in `fields.yaml`
- [ ] **CLI**: Command-line interface for generate/validate/publish/convert workflows
- [x] **Property annotations**: Add openMINDS property URIs to CEDAR fields (e.g., `https://openminds.om-i.org/props/species`)
