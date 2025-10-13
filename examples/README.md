# Examples

This directory contains example files demonstrating the openMINDS to CEDAR conversion.

## Files

### `example_subject.schema.omi.json`

Sample openMINDS schema for a Subject entity.

**Contents**:
- Fields: `age`, `biologicalSex`, `lookupLabel`, `species`, `studiedState`
- Demonstrates various field types: number, linked types, arrays
- Shows semantic connections via `_linkedTypes`

**Usage**:
```bash
# Convert this example schema
python src/main.py single examples/example_subject.schema.omi.json --name Subject
```

### `subject_cedar_element_FINAL.json`

Validated CEDAR Element generated from `example_subject.schema.omi.json`.

**Features**:
- ✅ Validated against CEDAR schema
- ✅ Successfully uploaded to CEDAR Workbench
- Contains 5 fields with proper ontology mappings:
  - `age`: Numeric field
  - `biologicalSex`: Controlled term (PATO ontology)
  - `lookupLabel`: Text field
  - `species`: Controlled term (NCBITAXON ontology)
  - `studiedState`: Multi-select controlled term

**Usage**:
This file can be directly uploaded to CEDAR Workbench:

```bash
# Via API
curl -X POST \
  https://resource.metadatacenter.org/template-elements \
  -H "Authorization: apiKey YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d @examples/subject_cedar_element_FINAL.json
```

Or via the CEDAR Workbench UI: Create → Element → Import from JSON

## Comparison

| Aspect | openMINDS Schema | CEDAR Element |
|--------|------------------|---------------|
| File size | 2.2 KB | 16.3 KB |
| Fields | 5 properties | 5 fields + metadata |
| Semantic types | `_linkedTypes` | Ontology constraints |
| Format | JSON Schema | JSON-LD |
| Purpose | Schema definition | Metadata authoring |

## Try It Yourself

1. **Inspect the openMINDS schema**:
```bash
python -m json.tool examples/example_subject.schema.omi.json
```

2. **Convert to CEDAR**:
```bash
python src/main.py single examples/example_subject.schema.omi.json --name ExampleSubject --output-dir output/examples
```

3. **Compare input and output**:
```bash
# Input
wc -l examples/example_subject.schema.omi.json

# Output
wc -l output/examples/examplesubject_element.json
```

4. **Validate the structure** (using the demo notebook):
```bash
jupyter notebook cedar_element_demo.ipynb
```
