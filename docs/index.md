# openminds2cedar Documentation

This library generates CEDAR metadata templates from openMINDS schemas and converts filled CEDAR instances back to validated openMINDS collections.

## Installation

```bash
uv sync
cp .env.example .env  # Add your CEDAR_API_KEY
```

## Quick Start

```python
from openminds2cedar.generators import CEDARElementGenerator, CEDARTemplateGenerator
from openminds2cedar.converters import CEDARToOpenMINDSConverter
from openminds2cedar.api import CEDARClient

# Generate and upload a Subject element
gen = CEDARElementGenerator()
element = gen.generate("core.Subject")

client = CEDARClient()
client.upload(element, "element")

# Convert a filled instance back to openMINDS
converter = CEDARToOpenMINDSConverter()
collection = converter.convert("instance.json")
```

## Module Guide

### Registry (`src/openminds2cedar/registry/`)

Configuration files that define what schemas and fields are supported.

**schemas.yaml** lists openMINDS schemas organized by module:
```yaml
schemas:
  core: [Subject, SubjectState, Person, Dataset, ...]
```

**fields.yaml** maps field names to controlled term classes. This tells the element generator which fields should have dropdown options:
```yaml
controlled_terms:
  species: controlled_terms.Species
  biological_sex: controlled_terms.BiologicalSex
```

**templates.yaml** defines template compositions - which elements to combine and their cardinalities:
```yaml
templates:
  subject-study:
    elements: [core.Subject, core.SubjectState]
    cardinalities: [false, true]  # Subject=single, SubjectState=multiple
```

### Generators (`src/openminds2cedar/generators/`)

Create CEDAR JSON structures from openMINDS schemas.

**CEDARElementGenerator** introspects an openMINDS class (e.g., `om.core.Subject`) and generates a CEDAR TemplateElement. It iterates over the class properties, creates appropriate field types, and populates controlled term options from the openMINDS instance library.

**CEDARTemplateGenerator** combines multiple elements into a CEDAR Template. It handles cardinality (single vs multiple) by wrapping elements in arrays when needed.

**CEDARInstanceGenerator** creates instance payloads for testing. It takes a template and field values, producing valid CEDAR instance JSON.

### Converters (`src/openminds2cedar/converters/`)

Convert CEDAR instances back to openMINDS objects.

**TYPE_REGISTRY** is a dictionary built at import time that maps openMINDS type URIs to their Python classes. For example, `"https://openminds.om-i.org/types/Subject"` maps to `om.core.Subject`. This enables dynamic type resolution without hardcoding.

**CEDARToOpenMINDSConverter** performs the conversion in three steps:

1. **Type Resolution**: Reads the instance `@context` to find type URIs, then looks up the corresponding class in TYPE_REGISTRY.

2. **Property Mapping**: Iterates over the class properties and extracts values from the CEDAR data. For controlled terms (identified by having a `by_name` method), it resolves the string value to an openMINDS instance.

3. **Object Linking**: Introspects each object's properties to find links that should connect to other converted objects. If `Subject.studied_states` accepts `SubjectState` and we converted SubjectState objects, they get linked automatically.

**Resolver** provides utility methods for looking up controlled terms and classes by various identifiers.

### API (`src/openminds2cedar/api/`)

**CEDARClient** wraps the CEDAR Workbench REST API. It handles authentication, resource CRUD operations, validation, and folder management. Key methods:

- `upload(data, resource_type)` - Upload element/template/instance
- `validate(data, resource_type)` - Validate without uploading
- `sync_to_local(path)` - Download all resources to local files
- `clear_all()` - Delete all resources (for testing)

## Field Naming Convention

The library uses **snake_case** field names throughout, matching the openMINDS Python API. This means `biological_sex` rather than `biologicalSex`. This eliminates the need for case transformation - CEDAR field names map directly to openMINDS constructor parameters.

## Testing

```bash
uv run pytest tests/ -v
```

For manual end-to-end testing:
```bash
uv run python scripts/publish_test_resources.py
```

This clears CEDAR, uploads fresh elements/templates/instances, converts them back, and validates with openMINDS.
