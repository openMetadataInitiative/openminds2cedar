# Registry

Schema and field configuration in YAML format.

## Files

- `schemas.yaml` - Which openMINDS schemas to generate
- `fields.yaml` - Field-level configuration (URIs, term classes)

## Adding a New Schema

Edit `schemas.yaml`:

```yaml
schemas:
  core:
    - Subject        # existing
    - NewSchema      # add here
```

## Adding a Field

Edit `fields.yaml`:

```yaml
fields:
  newField:
    property_uri: https://openminds.om-i.org/props/newField
    term_class: controlled_terms.NewTermClass  # if controlled term
    # or
    field_type: text  # for free text
```

## Usage

```python
from openminds2cedar.registry import Registry

reg = Registry()
print(reg.schemas)           # ['core.Subject', ...]
print(reg.field("species"))  # {'property_uri': ..., 'term_class': ...}
```
