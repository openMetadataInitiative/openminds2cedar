# User Guide

This guide covers both developer and curator workflows for working with openminds2cedar.

## Developer Workflow

Developers generate CEDAR elements and templates from openMINDS schemas, then publish them for researchers to use.

### Generating Elements

Use the Python API to generate CEDAR template elements:

```python
from openminds2cedar.generators import CEDARElementGenerator

gen = CEDARElementGenerator()
element = gen.generate("core.Subject")

# Save locally for inspection
import json
with open("output/elements/subject.json", "w") as f:
    json.dump(element, f, indent=2)
```

The generator introspects the openMINDS Python class, creates appropriate field types, and populates controlled term dropdowns from the openMINDS instance library.

### Creating Templates

Templates combine multiple elements. Use the template generator to compose them:

```python
from openminds2cedar.generators import CEDARTemplateGenerator

# Create template referencing uploaded element IDs
template_gen = CEDARTemplateGenerator()
template = template_gen.generate(
    elements=[subject_element, subjectstate_element],
    element_ids=[subject_id, subjectstate_id],
    name="subject-study",
    description="Subject with state recordings"
)
```

### Publishing to CEDAR

Upload elements and templates via the CEDAR API:

```python
from openminds2cedar.api import CEDARClient

client = CEDARClient()

# Upload element, get back CEDAR ID
result = client.upload(element, "element")
element_id = result["id"]

# Upload template (after elements exist)
client.upload(template, "template")
```

### Testing Workflow

For end-to-end testing, use the manual test script:

```bash
uv run python scripts/publish_test_resources.py
```

This clears the CEDAR test folder, uploads fresh elements/templates/instances, converts them back to openMINDS, and validates the results.

## Curator Workflow

Curators convert filled CEDAR instances (from researchers) back to validated openMINDS collections.

### Converting Instances

The converter uses the `@context` mapping to determine openMINDS types dynamically:

```python
from openminds2cedar.converters import CEDARToOpenMINDSConverter

converter = CEDARToOpenMINDSConverter()
collection = converter.convert("instance.json")

# Validate each object
for obj in collection:
    errors = obj.validate()
    if errors:
        print(f"Validation failed: {errors}")

# Save as JSON-LD
collection.save("output/openminds/")
```

The converter handles:
- **Type resolution**: Reads `@context` to map element names to openMINDS classes
- **Controlled terms**: Resolves string values like "Mus musculus" to `om.controlled_terms.Species` instances
- **Object linking**: Automatically connects related objects (e.g., Subject to SubjectState)

### Fetching from CEDAR

To convert an instance stored on CEDAR:

```python
client = CEDARClient()
instance = client.get_instance("https://repo.metadatacenter.org/template-instances/xxx")

converter = CEDARToOpenMINDSConverter()
collection = converter.convert_instance(instance)
```

## Testing

Run the test suite:

```bash
uv run pytest tests/ -v
```

Tests use shared fixtures from `tests/fixtures/__init__.py` which serve as the single source of truth for mock data. The fixtures include:
- `MOCK_SUBJECT_DATA`, `MOCK_SUBJECTSTATE_DATA` - Field values
- `sample_cedar_instance()` - Complete Subject+SubjectState instance
- `person_instance()`, `tissue_sample_instance()` - Additional type tests

## Configuration

Set up your environment:

```bash
cp .env.example .env
# Edit .env with your CEDAR API key and folder IDs
```

Required variables:
- `CEDAR_API_KEY` - Your CEDAR Workbench API key
- `CEDAR_FOLDER_ELEMENTS` - Folder for published elements
- `CEDAR_FOLDER_TEMPLATES` - Folder for published templates
- `CEDAR_FOLDER_INSTANCES` - Folder for researcher instances
