# Field Mapping Guide

Complete guide to how openMINDS fields are mapped to CEDAR fields.

## Overview

The converter analyzes each openMINDS field specification and determines the appropriate CEDAR field type based on:
1. JSON Schema `type` property
2. Presence of `_linkedTypes` (semantic connections)
3. `format` property (e.g., "iri")
4. Array item specifications

## Mapping Rules

### Rule 1: Numeric Fields

**openMINDS Pattern**:
```json
{
  "type": "number"
}
```
or
```json
{
  "type": "integer"
}
```

**CEDAR Output**:
```json
{
  "@type": "https://schema.metadatacenter.org/core/TemplateField",
  "_ui": {
    "inputType": "numeric"
  },
  "_valueConstraints": {
    "requiredValue": false,
    "numberType": "xsd:decimal"
  },
  "properties": {
    "@value": {"type": ["string", "null"]},
    "rdfs:label": {"type": ["string", "null"]},
    "@type": {"type": "string", "format": "uri"}
  }
}
```

**Example openMINDS Fields**:
- `age` (type: number)
- `weight` (type: number)
- `count` (type: integer)

---

### Rule 2: Controlled Term Fields (with _linkedTypes)

**openMINDS Pattern**:
```json
{
  "type": "string",
  "_linkedTypes": ["BiologicalSex"]
}
```

**CEDAR Output**:
```json
{
  "@type": "https://schema.metadatacenter.org/core/TemplateField",
  "_ui": {
    "inputType": "textfield"
  },
  "_valueConstraints": {
    "requiredValue": false,
    "ontologies": [],
    "valueSets": [],
    "classes": [],
    "branches": [
      {
        "source": "Phenotype And Trait Ontology (PATO)",
        "acronym": "PATO",
        "uri": "http://purl.obolibrary.org/obo/PATO_0000047",
        "name": "biological sex",
        "maxDepth": 0
      }
    ],
    "multipleChoice": false
  },
  "properties": {
    "@type": {...},
    "rdfs:label": {"type": ["string", "null"]},
    "@id": {"type": "string", "format": "uri"}
  }
}
```

**Ontology Mappings**:

| _linkedTypes Value | Ontology | URI |
|-------------------|----------|-----|
| `BiologicalSex` | PATO | http://purl.obolibrary.org/obo/PATO_0000047 |
| `Species` | NCBITAXON | https://data.bioontology.org/ontologies/NCBITAXON |

---

### Rule 3: IRI Format Fields

**openMINDS Pattern**:
```json
{
  "type": "string",
  "format": "iri"
}
```

**CEDAR Output**:
Similar to controlled term field, but without specific ontology constraints (empty ontologies list).

**Example openMINDS Fields**:
- `studiedState` (linked to SubjectState)
- `affiliation` (linked to Organization)

---

### Rule 4: Array Fields (Multiple Values)

**openMINDS Pattern**:
```json
{
  "type": "array",
  "items": {
    "type": "string",
    "format": "iri"
  }
}
```

**CEDAR Output**:
```json
{
  "@type": "https://schema.metadatacenter.org/core/TemplateField",
  "_ui": {
    "inputType": "textfield"
  },
  "_valueConstraints": {
    "requiredValue": false,
    "ontologies": [],
    "valueSets": [],
    "classes": [],
    "branches": [],
    "multipleChoice": true  // <-- Key difference
  }
}
```

**Example openMINDS Fields**:
- `keywords` (array of strings)
- `authors` (array of Person IRIs)

---

### Rule 5: Simple Text Fields

**openMINDS Pattern**:
```json
{
  "type": "string"
}
```

**CEDAR Output**:
```json
{
  "@type": "https://schema.metadatacenter.org/core/TemplateField",
  "_ui": {
    "inputType": "textfield"
  },
  "_valueConstraints": {
    "requiredValue": false
  },
  "properties": {
    "@type": {...},
    "@value": {"type": ["string", "null"]},
    "rdfs:label": {"type": ["string", "null"]}
  }
}
```

**Example openMINDS Fields**:
- `name` (type: string)
- `description` (type: string)
- `identifier` (type: string)

---

## Complete Field Examples

### Example 1: Subject Schema

**openMINDS Input** (`subject.schema.omi.json`):
```json
{
  "type": "object",
  "properties": {
    "age": {
      "type": "number",
      "description": "Age of the subject"
    },
    "biologicalSex": {
      "type": "string",
      "_linkedTypes": ["BiologicalSex"],
      "description": "Biological sex of the subject"
    },
    "lookupLabel": {
      "type": "string",
      "description": "Lookup label for the subject"
    },
    "species": {
      "type": "string",
      "_linkedTypes": ["Species"],
      "description": "Species of the subject"
    },
    "studiedState": {
      "type": "array",
      "items": {
        "type": "string",
        "format": "iri"
      },
      "_linkedTypes": ["SubjectState"],
      "description": "States of the subject"
    }
  },
  "required": ["biologicalSex", "species"]
}
```

**CEDAR Output Field Summary**:

| Field Name | openMINDS Type | CEDAR Input Type | Ontology | Multiple | Required |
|------------|----------------|------------------|----------|----------|----------|
| age | number | numeric | - | No | No |
| biologicalSex | string + _linkedTypes | textfield | PATO | No | Yes |
| lookupLabel | string | textfield | - | No | No |
| species | string + _linkedTypes | textfield | NCBITAXON | No | Yes |
| studiedState | array + IRI items | textfield | - | Yes | No |

---

### Example 2: Person Schema

**openMINDS Input** (`person.schema.omi.json`):
```json
{
  "type": "object",
  "properties": {
    "familyName": {
      "type": "string",
      "description": "Family name of the person"
    },
    "givenName": {
      "type": "string",
      "description": "Given name of the person"
    },
    "email": {
      "type": "string",
      "format": "email",
      "description": "Email address"
    },
    "affiliation": {
      "type": "array",
      "items": {
        "type": "string",
        "format": "iri"
      },
      "_linkedTypes": ["Organization"],
      "description": "Affiliated organizations"
    }
  },
  "required": ["familyName", "givenName"]
}
```

**CEDAR Output Field Summary**:

| Field Name | openMINDS Type | CEDAR Input Type | Multiple | Required |
|------------|----------------|------------------|----------|----------|
| familyName | string | textfield | No | Yes |
| givenName | string | textfield | No | Yes |
| email | string (format: email) | textfield | No | No |
| affiliation | array + IRI | textfield | Yes | No |

---

## Field Metadata Mapping

### Description Fields

**openMINDS**:
```json
{
  "description": "Field description here"
}
```
or
```json
{
  "_instruction": "Instruction text here"
}
```

**CEDAR**:
```json
{
  "schema:description": "Field description here",
  "_ui": {
    "propertyDescriptions": {
      "fieldName": "Field description here"
    }
  }
}
```

The converter uses `description` if available, otherwise falls back to `_instruction`.

---

### Required Fields

**openMINDS**:
```json
{
  "required": ["biologicalSex", "species"]
}
```

**CEDAR** (element level):
```json
{
  "required": ["@context", "@id", "biologicalSex", "species"]
}
```

**CEDAR** (field level):
```json
{
  "_valueConstraints": {
    "requiredValue": true
  }
}
```

Note: `@context` and `@id` are always required in CEDAR elements.

---

## UI Configuration

### Property Labels

**openMINDS Field Name**: `biologicalSex`

**CEDAR UI Configuration**:
```json
{
  "_ui": {
    "propertyLabels": {
      "biologicalSex": "biologicalSex"
    }
  },
  "skos:prefLabel": "Biological Sex"  // At field level
}
```

The `skos:prefLabel` is auto-generated by capitalizing and spacing the field name.

---

### Field Ordering

**openMINDS**: Order determined by iteration over `properties` dictionary

**CEDAR**:
```json
{
  "_ui": {
    "order": ["age", "biologicalSex", "lookupLabel", "species", "studiedState"]
  }
}
```

Fields appear in CEDAR UI in this order.

---

## Advanced Mappings

### Custom Ontology Mapping

To add custom ontology mappings, edit `config.yaml`:

```yaml
ontology_mappings:
  customField:
    source: "My Ontology Name"
    acronym: "MYONTO"
    uri: "http://example.org/myonto/term"
    name: "Custom Term"
    maxDepth: 2
```

Then add detection logic in `cedar_element_generator.py`:

```python
def _create_controlled_term_field(self, ...):
    # ... existing code ...

    if any("CustomType" in lt for lt in linked_types):
        field["_valueConstraints"]["branches"].append({
            "source": "My Ontology Name",
            "acronym": "MYONTO",
            "uri": "http://example.org/myonto/term",
            "name": "Custom Term",
            "maxDepth": 2
        })
```

---

### Enum Fields

**openMINDS Pattern**:
```json
{
  "type": "string",
  "enum": ["value1", "value2", "value3"]
}
```

**Current Behavior**: Treated as text field (enums not explicitly mapped)

**Future Enhancement**: Could be mapped to CEDAR value sets:
```json
{
  "_valueConstraints": {
    "literals": [
      {"label": "value1"},
      {"label": "value2"},
      {"label": "value3"}
    ]
  }
}
```

---

### Complex Types (Objects, Nested Schemas)

**openMINDS Pattern**:
```json
{
  "type": "object",
  "properties": {
    "nestedField": {...}
  }
}
```

**Current Behavior**: Not supported (treated as text field)

**Recommendation**: Flatten nested structures or create separate CEDAR elements for complex types.

---

## Validation Constraints

### String Constraints

**openMINDS**:
```json
{
  "type": "string",
  "minLength": 3,
  "maxLength": 50,
  "pattern": "^[A-Z]"
}
```

**CEDAR**: Currently not mapped

**Future Enhancement**: Could use `_valueConstraints`:
```json
{
  "_valueConstraints": {
    "minLength": 3,
    "maxLength": 50
  }
}
```

---

### Numeric Constraints

**openMINDS**:
```json
{
  "type": "number",
  "minimum": 0,
  "maximum": 150
}
```

**CEDAR**: Currently not mapped

**Future Enhancement**: Could use `_valueConstraints`:
```json
{
  "_valueConstraints": {
    "numberType": "xsd:decimal",
    "minValue": 0,
    "maxValue": 150
  }
}
```

---

## Field Identifiers

### @id Generation

Every CEDAR field needs a unique `@id`:

```python
import uuid

field["@id"] = f"https://repo.metadatacenter.org/template-fields/{uuid.uuid4()}"
```

**Example**:
```json
{
  "@id": "https://repo.metadatacenter.org/template-fields/a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

This allows CEDAR to track and reuse field definitions across templates.

---

### Context Properties

Each field is also added to the element's `@context`:

```json
{
  "properties": {
    "@context": {
      "properties": {
        "biologicalSex": {
          "enum": ["https://schema.metadatacenter.org/properties/12345678-1234-1234-1234-123456789012"]
        }
      },
      "required": ["biologicalSex"]
    }
  }
}
```

This provides semantic grounding for the field in RDF/JSON-LD.

---

## Summary Table

| openMINDS Pattern | CEDAR Field Type | Input Type | Value Constraints |
|-------------------|------------------|------------|-------------------|
| `type: "string"` | TemplateField | textfield | - |
| `type: "number"` | TemplateField | numeric | numberType: xsd:decimal |
| `type: "integer"` | TemplateField | numeric | numberType: xsd:decimal |
| `_linkedTypes: ["BiologicalSex"]` | TemplateField | textfield | branches: [PATO] |
| `_linkedTypes: ["Species"]` | TemplateField | textfield | ontologies: [NCBITAXON] |
| `format: "iri"` | TemplateField | textfield | - |
| `type: "array"` + IRI items | TemplateField | textfield | multipleChoice: true |
| `type: "array"` + string items | TemplateField | textfield | - |

---

## Testing Field Mappings

To verify field mappings:

1. **Run conversion**:
```bash
python src/main.py single schemas/openminds/subject.schema.omi.json --name Subject
```

2. **Inspect output**:
```bash
python -m json.tool output/cedar_elements/subject_element.json | less
```

3. **Check specific field**:
```python
import json

with open("output/cedar_elements/subject_element.json") as f:
    element = json.load(f)

bio_sex_field = element["properties"]["biologicalSex"]
print(json.dumps(bio_sex_field, indent=2))
```

4. **Validate in CEDAR**: Upload to CEDAR Workbench and verify field rendering
