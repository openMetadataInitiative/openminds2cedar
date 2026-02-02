# Registry

Configuration for openMINDS schemas and controlled term fields.

## Files

- `schemas.yaml` - Which schemas to generate
- `fields.yaml` - Controlled term mappings

## Usage

```python
from openminds2cedar.registry import Registry

reg = Registry()
reg.schemas              # ['core.Subject', 'core.SubjectState', ...]
reg.has_field("species") # True (controlled term)
reg.field("species")     # {"term_class": "controlled_terms.Species"}
```

## Adding Fields

Only controlled term fields need configuration:

```yaml
controlled_terms:
  newField: controlled_terms.NewTermClass
```

Text fields are handled by default.
