# Converters Module

Convert CEDAR instances to openMINDS objects.

## CEDARToOpenMINDSConverter

```python
from openminds2cedar.converters import CEDARToOpenMINDSConverter

converter = CEDARToOpenMINDSConverter()
collection = converter.convert("data/cedar/instances/my_instance.json")

# Validate all objects
for obj in collection:
    failures = obj.validate()
    assert len(failures) == 0

# Save as JSON-LD
collection.save("output/openminds/")
```

## Resolver

Looks up controlled terms using `openminds.latest`.

```python
from openminds2cedar.converters import Resolver

resolver = Resolver()
resolver.lookup("controlled_terms.Species", "Mus musculus")
# Returns: {"id": "...", "name": "Mus musculus"}

resolver.get_options("controlled_terms.BiologicalSex")
# Returns: [{"label": "female", "id": "..."}, {"label": "male", "id": "..."}, ...]
```
