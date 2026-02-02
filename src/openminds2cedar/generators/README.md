# Generators

Create CEDAR elements and templates from openMINDS schemas.

## Element Generator

```python
from openminds2cedar.generators import CEDARElementGenerator

gen = CEDARElementGenerator()
element = gen.generate("core.Subject")
element = gen.generate("core.SubjectState")
```

## Template Generator

Combines elements into a template.

```python
from openminds2cedar.generators import CEDARTemplateGenerator

gen = CEDARTemplateGenerator()
template = gen.generate(
    elements=[subject_elem, state_elem],
    element_ids=[subject_elem["@id"], state_elem["@id"]],
    name="my-template",
    description="Template description"
)
```
