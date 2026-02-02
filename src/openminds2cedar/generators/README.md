# Generators Module

Create CEDAR elements and templates from openMINDS schemas.

## CEDARElementGenerator

```python
from openminds2cedar.generators import CEDARElementGenerator

gen = CEDARElementGenerator(client=client)
element = gen.generate("core.Subject")
element = gen.generate_and_validate("core.SubjectState")  # Raises on invalid
```

## CEDARTemplateGenerator

Combines uploaded elements into a template.

```python
from openminds2cedar.generators import CEDARTemplateGenerator
import json

# Load synced elements
elements, element_ids = [], []
for name in ["subject", "subjectstate"]:
    with open(f"data/cedar/elements/{name}.json") as f:
        elem = json.load(f)
    elements.append(elem)
    element_ids.append(elem["@id"])

# Generate and upload
gen = CEDARTemplateGenerator()
template = gen.generate(elements, element_ids, "my-template", "Description")
client.upload_template(template)
```
