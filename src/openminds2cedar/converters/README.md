# Converters Module

Convert CEDAR instances to openMINDS objects using dynamic type resolution.

## CEDARToOpenMINDSConverter

Generic converter that uses `@context` to determine openMINDS types:

```python
from openminds2cedar.converters import CEDARToOpenMINDSConverter

converter = CEDARToOpenMINDSConverter()
collection = converter.convert("instance.json")

# Works with any openMINDS type (Subject, Person, TissueSample, etc.)
for obj in collection:
    assert not obj.validate()
```

## TYPE_REGISTRY

Maps type URIs to openMINDS classes (built at import time):

```python
from openminds2cedar.converters.resolver import TYPE_REGISTRY

TYPE_REGISTRY["https://openminds.om-i.org/types/Subject"]  # -> om.core.Subject
TYPE_REGISTRY["https://openminds.om-i.org/types/Person"]   # -> om.core.Person
```

## Resolver

Looks up controlled terms and classes:

```python
from openminds2cedar.converters import Resolver

resolver = Resolver()
resolver.get_class_by_type_uri("https://openminds.om-i.org/types/Subject")
resolver.lookup("controlled_terms.Species", "Mus musculus")
```
