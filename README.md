# openminds2cedar

Generate CEDAR template elements from openMINDS schemas and convert filled instances back to openMINDS-LD.

## Quick Start

```bash
uv sync
cp .env.example .env  # Edit with your CEDAR API key
```

## CLI Commands

```bash
# Developer: generate, template, validate
uv run openminds2cedar generate core.Subject
uv run openminds2cedar template my-template output/elements/core/*.json
uv run openminds2cedar validate output/

# Publish when ready
uv run openminds2cedar publish output/elements/

# Curator: convert by instance ID
uv run openminds2cedar convert https://repo.metadatacenter.org/template-instances/xxx

# Utilities
uv run openminds2cedar sync     # Sync all CEDAR resources locally
```

## Workflows

### Developer Workflow

Generate CEDAR elements from openMINDS schemas, validate, and publish:

```bash
# 1. Generate and validate elements
uv run openminds2cedar generate core.Subject
uv run openminds2cedar generate core.SubjectState
uv run openminds2cedar validate output/elements/

# 2. Publish elements to CEDAR
uv run openminds2cedar publish output/elements/

# 3. Sync to get real element IDs
uv run openminds2cedar sync -o data/cedar

# 4. Create template using synced elements (with real IDs)
uv run openminds2cedar template subject-study \
    data/cedar/elements/subject.json \
    data/cedar/elements/subjectstate.json

# 5. Validate and publish template
uv run openminds2cedar validate output/templates/
uv run openminds2cedar publish output/templates/
```

**Note**: Templates created from local elements use placeholder IDs and cannot be validated until elements are published. Use synced elements to create templates with real CEDAR IDs.

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

Registry files (schema/field config):
- `registry/schemas.yaml` - Which openMINDS schemas to generate
- `registry/fields.yaml` - Field mappings and controlled term classes

## Roadmap

- [ ] **Schema coverage**: Expand beyond Subject/SubjectState to all openMINDS modules
- [ ] **Declarative UI**: Configure field UI (inputType, help text) in `fields.yaml`
- [ ] **Template composition**: Define templates in YAML with element references
- [ ] **Generic converter**: Schema-driven conversion using `@context` types (not hardcoded)
