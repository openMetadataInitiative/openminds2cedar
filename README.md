# openminds2cedar

Generate CEDAR template elements from openMINDS schemas and convert filled instances back to openMINDS-LD.

## Quick Start

```bash
# Install
uv sync

# Set CEDAR API key
export CEDAR_API_KEY="your-api-key"

# Run tests
uv run pytest tests/ -v
```

## Workflow

1. **Generate elements** from openMINDS schemas
2. **Upload** to CEDAR Workbench
3. **Create template** combining elements (via UI or programmatically)
4. **Fill instances** in CEDAR
5. **Convert** filled instances to openMINDS-LD

## Usage Examples

### Generate and upload elements

```python
from openminds2cedar.generators import CEDARElementGenerator
from openminds2cedar.api import CEDARClient

client = CEDARClient()
gen = CEDARElementGenerator(client=client)

# Generate and validate
element = gen.generate("core.Subject")
result = client.validate(element)

# Upload
if result["valid"]:
    result = client.upload(element)
    print(f"Uploaded: {result['id']}")
```

### Create template from elements

```python
from openminds2cedar.generators import CEDARTemplateGenerator

gen = CEDARTemplateGenerator()
template = gen.generate(elements, element_ids, "my-template", "Description")
client.upload_template(template)
```

### Convert CEDAR instance to openMINDS

```python
from openminds2cedar.converters import CEDARToOpenMINDSConverter

converter = CEDARToOpenMINDSConverter()
collection = converter.convert("data/cedar/instances/my_instance.json")

# Validate and save
for obj in collection:
    assert len(obj.validate()) == 0
collection.save("output/openminds/")
```

### Sync CEDAR data locally

```python
client = CEDARClient()
client.sync_to_local("data/cedar")  # Syncs elements, templates, instances
```

## Project Structure

```
src/openminds2cedar/
├── api/            # CEDAR Workbench API client
├── converters/     # CEDAR → openMINDS conversion
├── generators/     # CEDAR element/template generation
└── registry/       # Schema and field configuration (YAML)

data/cedar/         # Synced CEDAR resources
├── elements/
├── templates/
└── instances/
```

## Configuration

Copy `.env.example` to `.env` and set:

```bash
CEDAR_API_KEY=your-api-key
CEDAR_FOLDER_ELEMENTS=https://repo.metadatacenter.org/folders/your-folder-id
CEDAR_FOLDER_TEMPLATES=https://repo.metadatacenter.org/folders/your-folder-id
CEDAR_FOLDER_INSTANCES=https://repo.metadatacenter.org/folders/your-folder-id
```

Registry files (schema/field config):
- `registry/schemas.yaml` - Which openMINDS schemas to generate
- `registry/fields.yaml` - Field mappings and controlled term classes
