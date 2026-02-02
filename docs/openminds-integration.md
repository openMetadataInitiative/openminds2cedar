# openMINDS Integration

Technical overview for openMINDS developers explaining how this tool bridges openMINDS and CEDAR.

## The Problem

Researchers need to enter metadata. CEDAR Workbench provides a web UI with forms, validation, and controlled term dropdowns. But CEDAR doesn't know about openMINDS schemas. This tool:

1. **Generates CEDAR templates** from openMINDS schemas (so researchers get forms)
2. **Converts filled instances** back to openMINDS JSON-LD (so data curators get validated collections)

## How We Use the openMINDS Python Package

The tool relies entirely on `openminds.latest` for schema introspection and controlled term resolution. No hardcoded type lists.

### Schema Introspection

```python
import openminds.latest as om

# Get class and iterate properties
subject_class = om.core.Subject
for prop in subject_class.properties:
    print(prop.name)       # "biological_sex", "species", etc. (snake_case)
    print(prop.is_link)    # True if links to another type
    print(prop.multiple)   # True if accepts list
    print(prop.types)      # List of allowed types for this property
```

This lets us generate CEDAR fields dynamically without maintaining separate schema definitions.

### Controlled Term Resolution

```python
# Get all instances of a controlled term
for species in om.controlled_terms.Species.instances():
    print(species.name, species.id)

# Lookup by name (used during conversion)
mouse = om.controlled_terms.Species.by_name("Mus musculus")
```

We use `instances()` to populate CEDAR dropdowns and `by_name()` to resolve user selections back to openMINDS objects.

### Type Registry

At import time, we build a mapping of type URIs to Python classes:

```python
# resolver.py
TYPE_REGISTRY = {
    "https://openminds.om-i.org/types/Subject": om.core.Subject,
    "https://openminds.om-i.org/types/Person": om.core.Person,
    # ... all types from all modules
}
```

This enables generic type resolution from CEDAR instance `@context` without hardcoding.

## Concept Mapping

| openMINDS | CEDAR | Notes |
|-----------|-------|-------|
| Schema (e.g., `core.Subject`) | TemplateElement | One element per schema |
| Property | Field | Text, radio, checkbox, dropdown |
| Controlled term class | Field with options | Options from `instances()` |
| Linked type | Nested element or reference | Templates compose elements |
| Collection | Instance | Filled form with all elements |

## The Generic Converter

The converter in [cedar_to_openminds.py](../src/openminds2cedar/converters/cedar_to_openminds.py) works with any openMINDS type through three mechanisms:

### 1. Type Resolution via @context

CEDAR instances include a `@context` mapping element names to type URIs:

```json
{
  "@context": {
    "subject": "https://openminds.om-i.org/types/Subject",
    "subjectstate": "https://openminds.om-i.org/types/SubjectState"
  },
  "subject": { ... },
  "subjectstate": { ... }
}
```

The converter reads this to determine which openMINDS class to instantiate.

### 2. Property Iteration

For each element, we iterate the class properties and extract values:

```python
for prop in om_class.properties:
    value = self._extract_property_value(data, prop, converted_objects)
    if value is not None:
        kwargs[prop.name] = value

return om_class(**kwargs)
```

### 3. Controlled Term Detection

Properties that link to controlled terms are identified by the `by_name` method:

```python
for allowed_type in prop.types:
    if hasattr(allowed_type, "by_name"):
        # It's a controlled term - resolve string to instance
        result = allowed_type.by_name(raw_value)
```

### 4. Object Linking via Introspection

After converting all elements, we link related objects by checking property type compatibility:

```python
# Build map of class -> converted objects
linkable = {type(obj): [obj, ...] for obj in converted}

# For each object, check its link properties
for prop in cls.properties:
    if prop.is_link:
        for allowed_type in prop.types:
            if allowed_type in linkable:
                setattr(obj, prop.name, linkable[allowed_type])
```

This automatically connects `Subject.studied_states` to converted `SubjectState` objects without hardcoding relationships.

## Field Naming Convention

We use **snake_case** throughout, matching the openMINDS Python API:

- `biological_sex` (not `biologicalSex`)
- `internal_identifier` (not `internalIdentifier`)

This means CEDAR field names map directly to constructor parameters with no transformation.

## Adding New Types

To support a new openMINDS type:

1. Add to `registry/schemas.yaml`:
   ```yaml
   schemas:
     core:
       - NewType
   ```

2. Map controlled term fields in `registry/fields.yaml`:
   ```yaml
   controlled_terms:
     new_field: controlled_terms.SomeTermClass
   ```

The converter handles it automatically via type introspection.

## Validation

Converted objects are validated using openMINDS's built-in validator:

```python
collection = converter.convert(instance)
for obj in collection:
    errors = obj.validate()
    # Returns list of validation failures, empty if valid
```

## Limitations

- **Nested links**: Currently handles one level of object linking (e.g., Subject → SubjectState). Deeper nesting would need recursive handling.
- **Custom properties**: openMINDS properties not in the Python package won't be converted.
- **Version pinning**: Uses `openminds.latest` - specific version support could be added.
