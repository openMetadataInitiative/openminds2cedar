# Architecture

## System Overview

The openMINDS to CEDAR converter is designed as a modular pipeline with three main components:

```
┌─────────────────┐       ┌──────────────────┐       ┌─────────────────┐
│ Schema Fetcher  │──────▶│ Element Generator│──────▶│ Batch Converter │
└─────────────────┘       └──────────────────┘       └─────────────────┘
        │                          │                          │
        ▼                          ▼                          ▼
  openMINDS Schemas         Single Element             CEDAR Elements
  (JSON Schema)             (CEDAR JSON-LD)            + Reports
```

## Component Details

### 1. Schema Fetcher (`schema_fetcher.py`)

**Purpose**: Download openMINDS schemas from GitHub repository

**Key Classes**:
- `OpenMINDSSchemaFetcher`: Handles HTTP requests and file I/O

**Responsibilities**:
- Fetch schemas from configurable GitHub URL
- Save schemas to local filesystem
- Handle network errors gracefully

**Configuration**: Uses `config.yaml` for:
- `openminds.github_base_url`: Base URL for schema repository
- `openminds.core_schemas`: List of schemas to fetch

### 2. CEDAR Element Generator (`cedar_element_generator.py`)

**Purpose**: Core conversion logic from openMINDS to CEDAR

**Key Classes**:
- `CEDARElementGenerator`: Main converter class

**Responsibilities**:
- Parse openMINDS JSON Schema
- Generate CEDAR Element structure
- Create CEDAR fields with appropriate types
- Map ontologies based on field semantics
- Generate UUIDs for field identifiers

**Field Type Mapping Logic**:

```python
if field_type == "number" or field_type == "integer":
    return _create_numeric_field()
elif "_linkedTypes" in field_spec or field_spec.get("format") == "iri":
    return _create_controlled_term_field()
elif field_type == "array":
    if items_format == "iri":
        return _create_controlled_term_field(multiple=True)
    else:
        return _create_text_field()
else:
    return _create_text_field()
```

**Ontology Mapping**:
- BiologicalSex → PATO (Phenotype and Trait Ontology)
- Species → NCBITAXON (NCBI Taxonomy)
- Custom mappings configurable in `config.yaml`

### 3. Batch Converter (`batch_converter.py`)

**Purpose**: Orchestrate batch processing of multiple schemas

**Key Classes**:
- `BatchConverter`: Batch processing orchestrator

**Responsibilities**:
- Discover schema files using glob patterns
- Convert each schema using `CEDARElementGenerator`
- Generate conversion reports
- Print summary statistics

**Output**:
- Individual CEDAR element JSON files
- `conversion_report.json` with statistics

### 4. Main CLI (`main.py`)

**Purpose**: User-facing command-line interface

**Commands**:
- `fetch`: Download schemas
- `convert`: Convert existing schemas
- `all`: Fetch and convert in one step
- `single`: Convert a single schema file

**Argument Parsing**: Uses `argparse` with subcommands

## Data Flow

### Complete Workflow (fetch → convert)

```
User runs: python src/main.py all

1. SchemaFetcher.fetch_all_core_schemas()
   ├─ Read config.yaml for schema list
   ├─ Download each schema from GitHub
   └─ Save to schemas/openminds/

2. BatchConverter.convert_all()
   ├─ Glob for *.schema.omi.json files
   ├─ For each schema:
   │  ├─ Load JSON
   │  ├─ CEDARElementGenerator.create_element_from_openminds()
   │  │  ├─ Parse properties
   │  │  ├─ Detect field types
   │  │  ├─ Map ontologies
   │  │  └─ Generate CEDAR JSON-LD
   │  └─ Save element JSON
   ├─ Generate conversion_report.json
   └─ Print summary

Output: CEDAR elements in output/cedar_elements/
```

## CEDAR Element Structure

### Element-level Properties

```json
{
  "@type": "https://schema.metadatacenter.org/core/TemplateElement",
  "@context": { /* JSON-LD context */ },
  "@id": null,  // Null for creation, populated by CEDAR on upload
  "type": "object",
  "title": "Element title",
  "description": "Element description",
  "properties": { /* Field definitions */ },
  "_ui": {
    "order": ["field1", "field2"],
    "propertyLabels": {"field1": "Field 1"},
    "propertyDescriptions": {"field1": "Description"}
  },
  "required": ["@context", "@id"],
  "schema:name": "element-name",
  "schema:description": "Description",
  "pav:version": "0.0.1",
  "bibo:status": "bibo:draft",
  "schema:schemaVersion": "1.6.0",
  "$schema": "http://json-schema.org/draft-04/schema#"
}
```

### Field-level Properties

Each field in `properties` is a `TemplateField`:

```json
{
  "@type": "https://schema.metadatacenter.org/core/TemplateField",
  "@context": { /* Field context */ },
  "@id": "https://repo.metadatacenter.org/template-fields/<UUID>",
  "type": "object",
  "title": "field schema",
  "_ui": {
    "inputType": "textfield"  // or "numeric", "link", etc.
  },
  "_valueConstraints": {
    "requiredValue": true,
    "ontologies": [],  // For controlled terms
    "branches": [],    // For ontology branches
    "multipleChoice": false
  },
  "properties": {
    "@type": { /* URI type */ },
    "@value": {"type": ["string", "null"]},
    "rdfs:label": {"type": ["string", "null"]}
  },
  "schema:name": "fieldName",
  "schema:description": "Description",
  "skos:prefLabel": "Field Name"
}
```

## Configuration System

### config.yaml Structure

```yaml
cedar:
  version: "1.6.0"  # CEDAR schema version

openminds:
  github_base_url: "https://raw.githubusercontent.com/..."
  core_schemas:     # List of schemas to fetch
    - subject.schema.omi.json

directories:
  schemas: "schemas/openminds"
  output: "output/cedar_elements"

ontology_mappings:
  biologicalSex:    # Field name → ontology mapping
    source: "Phenotype And Trait Ontology (PATO)"
    acronym: "PATO"
    uri: "http://purl.obolibrary.org/obo/PATO_0000047"
```

## Extension Points

### Adding New Field Types

To add a new CEDAR field type:

1. Create method in `CEDARElementGenerator`:
```python
def _create_custom_field(self, field_name, description, is_required):
    # Field structure here
    return field
```

2. Add detection logic in `_create_cedar_field()`:
```python
elif field_spec.get("customProperty"):
    return self._create_custom_field(...)
```

### Adding New Ontology Mappings

1. Add to `config.yaml`:
```yaml
ontology_mappings:
  customField:
    acronym: "ONTO"
    name: "Custom Ontology"
    uri: "http://example.org/ontology"
```

2. Add mapping logic in `_create_controlled_term_field()`:
```python
if any("CustomType" in lt for lt in linked_types):
    field["_valueConstraints"]["ontologies"].append({
        "acronym": "ONTO",
        "name": "Custom Ontology",
        "uri": "http://example.org/ontology"
    })
```

### Adding New CLI Commands

1. Add subparser in `main.py`:
```python
custom_parser = subparsers.add_parser('custom', help='Custom command')
```

2. Add command handler:
```python
def custom_command(args):
    # Implementation
    pass
```

3. Add to command routing:
```python
elif args.command == 'custom':
    success = custom_command(args)
```

## Error Handling

### Schema Fetcher
- Network errors: Graceful degradation, continue with other schemas
- Invalid URLs: Clear error message with URL

### Element Generator
- Invalid JSON: Catch `json.JSONDecodeError`, log filename
- Missing properties: Use defaults, log warning
- Unsupported field types: Fall back to text field

### Batch Converter
- Per-schema try/catch: One failed schema doesn't stop batch
- Error tracking: All errors recorded in conversion report

## Performance Considerations

### Memory
- Streaming not implemented (all schemas loaded into memory)
- Suitable for typical use cases (< 100 schemas)
- For very large batches, consider implementing streaming

### Network
- Sequential downloads (no parallel fetching)
- Could be parallelized with `concurrent.futures` if needed

### File I/O
- JSON pretty-printing with indent=2 (human-readable)
- For production, could use compact JSON

## Testing Strategy

### Unit Tests
- Test each field type conversion
- Test ontology mapping logic
- Test error handling

### Integration Tests
- End-to-end conversion of sample schemas
- Validate output against CEDAR schema
- Test CLI commands

### Validation Tests
- Upload to CEDAR API (requires credentials)
- Verify element can be opened in CEDAR Workbench
