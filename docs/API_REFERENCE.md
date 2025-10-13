# API Reference

Complete API documentation for the openMINDS to CEDAR converter.

## Core Modules

### `cedar_element_generator.py`

#### Class: `CEDARElementGenerator`

Main converter class for transforming openMINDS schemas to CEDAR elements.

##### Constructor

```python
CEDARElementGenerator(cedar_version: str = "1.6.0")
```

**Parameters**:
- `cedar_version` (str): CEDAR schema version to use. Default: "1.6.0"

**Example**:
```python
generator = CEDARElementGenerator(cedar_version="1.6.0")
```

---

##### Method: `create_element_from_openminds`

```python
create_element_from_openminds(
    openminds_schema: Dict,
    element_name: Optional[str] = None
) -> Dict
```

Create a CEDAR Element from an openMINDS schema.

**Parameters**:
- `openminds_schema` (Dict): openMINDS schema dictionary (parsed JSON)
- `element_name` (Optional[str]): Custom name for the element. If None, uses schema title

**Returns**:
- `Dict`: CEDAR Element structure (JSON-LD dictionary)

**Example**:
```python
with open('subject.schema.omi.json') as f:
    schema = json.load(f)

element = generator.create_element_from_openminds(schema, "Subject")
```

---

##### Method: `save_element`

```python
save_element(element: Dict, output_path: str) -> None
```

Save CEDAR element to JSON file.

**Parameters**:
- `element` (Dict): CEDAR element dictionary
- `output_path` (str): Path to save the JSON file

**Example**:
```python
generator.save_element(element, "output/subject_element.json")
```

---

##### Private Method: `_create_cedar_field`

```python
_create_cedar_field(
    field_name: str,
    field_spec: Dict,
    is_required: bool
) -> Dict
```

Create a CEDAR field from openMINDS field specification.

**Parameters**:
- `field_name` (str): Name of the field
- `field_spec` (Dict): openMINDS field specification
- `is_required` (bool): Whether field is required

**Returns**:
- `Dict`: CEDAR TemplateField structure

**Field Type Detection Logic**:
1. If `type` is "number" or "integer" → numeric field
2. If `_linkedTypes` present or `format` is "iri" → controlled term field
3. If `type` is "array" with IRI items → multi-select controlled term field
4. Otherwise → text field

---

##### Private Method: `_create_text_field`

```python
_create_text_field(
    field_name: str,
    description: str,
    is_required: bool
) -> Dict
```

Create a CEDAR text field.

**Returns**: TemplateField with `inputType: "textfield"`

---

##### Private Method: `_create_numeric_field`

```python
_create_numeric_field(
    field_name: str,
    description: str,
    is_required: bool
) -> Dict
```

Create a CEDAR numeric field.

**Returns**: TemplateField with `inputType: "numeric"` and `numberType: "xsd:decimal"`

---

##### Private Method: `_create_controlled_term_field`

```python
_create_controlled_term_field(
    field_name: str,
    field_spec: Dict,
    description: str,
    is_required: bool,
    multiple: bool = False
) -> Dict
```

Create a CEDAR controlled term field (ontology-backed).

**Parameters**:
- `multiple` (bool): Whether field allows multiple values

**Returns**: TemplateField with ontology constraints

**Ontology Mapping**:
- `BiologicalSex` in `_linkedTypes` → PATO ontology branch
- `Species` in `_linkedTypes` → NCBITAXON ontology

---

### `batch_converter.py`

#### Class: `BatchConverter`

Convert multiple openMINDS schemas to CEDAR elements.

##### Constructor

```python
BatchConverter(
    input_dir: str = "schemas/openminds",
    output_dir: str = "output/cedar_elements",
    cedar_version: str = "1.6.0"
)
```

**Parameters**:
- `input_dir` (str): Directory containing openMINDS schemas
- `output_dir` (str): Directory to save CEDAR elements
- `cedar_version` (str): CEDAR schema version

**Example**:
```python
converter = BatchConverter(
    input_dir="schemas/openminds",
    output_dir="output/cedar_elements"
)
```

---

##### Method: `convert_schema`

```python
convert_schema(
    schema_path: Path,
    element_name: Optional[str] = None
) -> Optional[Dict]
```

Convert a single schema file.

**Parameters**:
- `schema_path` (Path): Path to openMINDS schema file
- `element_name` (Optional[str]): Custom name for element

**Returns**:
- `Optional[Dict]`: CEDAR element or None if failed

**Side Effects**:
- Saves element to `output_dir`
- Appends result to `self.results`

**Example**:
```python
from pathlib import Path

element = converter.convert_schema(
    Path("schemas/openminds/subject.schema.omi.json"),
    "Subject"
)
```

---

##### Method: `convert_all`

```python
convert_all(pattern: str = "*.schema.omi.json") -> List[Dict]
```

Convert all schemas matching pattern.

**Parameters**:
- `pattern` (str): Glob pattern for schema files

**Returns**:
- `List[Dict]`: List of CEDAR elements

**Side Effects**:
- Saves all elements to `output_dir`
- Prints conversion summary
- Saves conversion report to `output_dir/conversion_report.json`

**Example**:
```python
elements = converter.convert_all()
# or with custom pattern
elements = converter.convert_all(pattern="*subject*.schema.omi.json")
```

---

##### Attribute: `results`

```python
results: List[Dict]
```

List of conversion results. Each result contains:

```python
{
    'input_file': str,        # e.g., "subject.schema.omi.json"
    'output_file': str,       # e.g., "subject_element.json"
    'element_name': str,      # e.g., "Subject"
    'fields': int,            # Number of fields in element
    'required_fields': List[str],  # List of required field names
    'status': str            # "success" or "failed"
}
```

For failed conversions, includes `'error': str` with error message.

---

### `schema_fetcher.py`

#### Class: `OpenMINDSSchemaFetcher`

Fetch openMINDS schemas from GitHub repository.

##### Constructor

```python
OpenMINDSSchemaFetcher(
    output_dir: str = "schemas/openminds"
)
```

**Parameters**:
- `output_dir` (str): Directory to save downloaded schemas

**Example**:
```python
fetcher = OpenMINDSSchemaFetcher(output_dir="schemas/openminds")
```

---

##### Class Attribute: `BASE_URL`

```python
BASE_URL = "https://raw.githubusercontent.com/HumanBrainProject/openMINDS/v4/versions/core/"
```

Base URL for openMINDS core schemas.

---

##### Method: `fetch_schema`

```python
fetch_schema(schema_filename: str) -> Optional[Dict]
```

Fetch a single schema from GitHub.

**Parameters**:
- `schema_filename` (str): Filename (e.g., "subject.schema.omi.json")

**Returns**:
- `Optional[Dict]`: Schema dictionary or None if failed

**Side Effects**:
- Saves schema to `output_dir/schema_filename`

**Example**:
```python
schema = fetcher.fetch_schema("subject.schema.omi.json")
```

---

##### Method: `fetch_all_core_schemas`

```python
fetch_all_core_schemas() -> Dict[str, Dict]
```

Fetch all core schemas defined in config.

**Returns**:
- `Dict[str, Dict]`: Mapping of filename to schema dictionary

**Example**:
```python
schemas = fetcher.fetch_all_core_schemas()
# Returns: {
#   "subject.schema.omi.json": {...},
#   "person.schema.omi.json": {...},
#   ...
# }
```

---

## Convenience Functions

### `convert_openminds_to_cedar_element`

```python
convert_openminds_to_cedar_element(
    openminds_schema_path: str,
    output_path: str,
    element_name: Optional[str] = None
) -> Dict
```

Convenience function for single schema conversion.

**Parameters**:
- `openminds_schema_path` (str): Path to openMINDS JSON schema file
- `output_path` (str): Path to save the CEDAR element
- `element_name` (Optional[str]): Custom element name

**Returns**:
- `Dict`: CEDAR Element dictionary

**Example**:
```python
from src.cedar_element_generator import convert_openminds_to_cedar_element

element = convert_openminds_to_cedar_element(
    "schemas/openminds/subject.schema.omi.json",
    "output/subject_element.json",
    "Subject"
)
```

---

## CLI Interface

### `main.py`

Command-line interface implemented with `argparse`.

#### Commands

##### `fetch`

```bash
python src/main.py fetch [--schema-dir DIR]
```

Fetch openMINDS schemas from GitHub.

**Options**:
- `--schema-dir`: Directory for schemas (default: `schemas/openminds`)

---

##### `convert`

```bash
python src/main.py convert [--schema-dir DIR] [--output-dir DIR]
```

Convert existing schemas to CEDAR elements.

**Options**:
- `--schema-dir`: Input directory (default: `schemas/openminds`)
- `--output-dir`: Output directory (default: `output/cedar_elements`)

---

##### `all`

```bash
python src/main.py all [--schema-dir DIR] [--output-dir DIR]
```

Fetch and convert in one command (recommended).

---

##### `single`

```bash
python src/main.py single FILE [--name NAME] [--output-dir DIR]
```

Convert a single schema file.

**Arguments**:
- `FILE`: Path to schema file

**Options**:
- `--name`: Custom element name
- `--output-dir`: Output directory (default: `output/cedar_elements`)

---

## Data Structures

### openMINDS Schema Format

Expected input format:

```python
{
    "type": "object",
    "title": str,                    # Optional
    "description": str,              # Optional
    "properties": {
        "fieldName": {
            "type": str,             # "string", "number", "integer", "array"
            "description": str,      # Optional
            "_instruction": str,     # Optional
            "_linkedTypes": List[str],  # Optional, for semantic types
            "format": str,           # Optional, "iri" for linked data
            "items": {...}           # For array types
        }
    },
    "required": List[str]            # Optional
}
```

---

### CEDAR Element Format

Output format:

```python
{
    "@type": "https://schema.metadatacenter.org/core/TemplateElement",
    "@context": Dict,                 # JSON-LD context
    "@id": None,                      # Null for creation
    "type": "object",
    "title": str,
    "description": str,
    "properties": {
        "@context": {...},
        "@id": {...},
        "@type": {...},
        "fieldName": {                # TemplateField
            "@type": "https://schema.metadatacenter.org/core/TemplateField",
            "@id": str,               # UUID-based URI
            "_ui": {
                "inputType": str      # "textfield", "numeric", etc.
            },
            "_valueConstraints": {
                "requiredValue": bool,
                "ontologies": List,   # For controlled terms
                "branches": List,     # For ontology branches
                "multipleChoice": bool
            },
            ...
        }
    },
    "_ui": {
        "order": List[str],
        "propertyLabels": Dict[str, str],
        "propertyDescriptions": Dict[str, str]
    },
    "required": List[str],
    "schema:name": str,
    "schema:description": str,
    "pav:version": str,
    "bibo:status": str,
    "schema:schemaVersion": str,
    "$schema": str
}
```

---

### Conversion Report Format

Generated by `BatchConverter.convert_all()`:

```python
{
    "timestamp": str,                # ISO 8601 format
    "input_directory": str,
    "output_directory": str,
    "total_schemas": int,
    "successful": int,
    "failed": int,
    "results": List[Dict]            # See BatchConverter.results
}
```

---

## Error Handling

### Exceptions

The modules use standard Python exceptions:

- `FileNotFoundError`: Schema file not found
- `json.JSONDecodeError`: Invalid JSON in schema
- `KeyError`: Missing required property in schema
- `requests.RequestException`: Network error during fetch

### Error Recovery

- **Schema Fetcher**: Continues with remaining schemas if one fails
- **Batch Converter**: Records errors in report, continues batch
- **Element Generator**: Returns None on failure, logs error

---

## Type Hints

All modules use Python type hints for better IDE support:

```python
from typing import Dict, List, Optional
from pathlib import Path
```

---

## Usage Examples

### Complete Workflow

```python
from src.schema_fetcher import OpenMINDSSchemaFetcher
from src.batch_converter import BatchConverter

# 1. Fetch schemas
fetcher = OpenMINDSSchemaFetcher()
schemas = fetcher.fetch_all_core_schemas()
print(f"Fetched {len(schemas)} schemas")

# 2. Convert to CEDAR elements
converter = BatchConverter()
elements = converter.convert_all()
print(f"Converted {len(elements)} elements")

# 3. Check report
import json
with open("output/cedar_elements/conversion_report.json") as f:
    report = json.load(f)
print(f"Success rate: {report['successful']}/{report['total_schemas']}")
```

### Custom Processing

```python
from src.cedar_element_generator import CEDARElementGenerator
import json

generator = CEDARElementGenerator()

# Load and modify schema
with open("schemas/openminds/subject.schema.omi.json") as f:
    schema = json.load(f)

# Add custom processing
schema['properties']['customField'] = {
    "type": "string",
    "description": "My custom field"
}

# Convert
element = generator.create_element_from_openminds(schema, "CustomSubject")

# Modify element before saving
element['pav:version'] = "1.0.0"
element['bibo:status'] = "bibo:published"

# Save
generator.save_element(element, "output/custom_subject_element.json")
```
