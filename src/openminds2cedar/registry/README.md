# Registry

Configuration for openMINDS schemas, fields, and templates.

## Files

- `schemas.yaml` - Which schemas to generate (organized by module)
- `fields.yaml` - Field UI config: `input_type`, `term_class`, `help_text`, `multiple`
- `templates.yaml` - Template definitions with element cardinalities

## Usage

```python
from openminds2cedar.registry import Registry

reg = Registry()
reg.schemas                    # ['core.Subject', 'sands.BrainAtlas', ...]
reg.field("species")           # {"term_class": ..., "input_type": "list"}
reg.template("subject-study")  # {"elements": [...], "description": ...}
```

See `fields.yaml` for available input types and configuration options.
