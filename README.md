# openMINDS to CEDAR Converter

Converts openMINDS metadata schemas to CEDAR TemplateElements with automatic controlled vocabulary integration.

## Quick Start

```bash
# Setup
git clone <repository-url>
cd openminds2cedar
git submodule update --init --recursive
conda env create -f environment.yml
conda activate openminds2cedar

# Configure CEDAR API key
echo "CEDAR_API_KEY=your-key" > .env

# Generate CEDAR element
python main.py generate

# Validate and upload
python main.py validate
python main.py upload
```

## Features

- Automatic schema conversion from openMINDS to CEDAR
- Intelligent controlled vocabulary integration (81 types, 2,700+ instances)
- Smart UI selection: radio buttons for small lists, dropdowns for large lists
- CEDAR API validation and upload
- Full compliance with CEDAR Template Model v1.6.0

## Usage

### Generate Element

```python
from src.schema_loader import OpenMINDSSchemaLoader
from src.cedar_element_generator import CEDARElementGenerator

loader = OpenMINDSSchemaLoader()
schema = loader.load_schema('core', 'research', 'subject.schema.json')

generator = CEDARElementGenerator()
element = generator.create_element_from_openminds(schema, "Subject")
generator.save_element(element, 'output/subject.json')
```

### Validate and Upload

```python
from src.cedar_api import CEDARAPIClient

client = CEDARAPIClient()
validation = client.validate_element(element)
if validation.get('validates') == 'true':
    response = client.upload_element(element)
    print(f"Uploaded: {response.get('@id')}")
```

## Project Structure

```
openminds2cedar/
├── src/
│   ├── schema_loader.py           # Load openMINDS schemas
│   ├── cedar_element_generator.py # Convert to CEDAR format
│   ├── controlled_terms_loader.py # Load controlled vocabularies
│   └── cedar_api.py               # CEDAR API client
├── tests/                         # Test files
│   ├── test_generation.py         # Element generation test
│   └── test_validation.py         # CEDAR validation test
├── notebooks/
│   └── demo.qmd                   # Comprehensive demo
├── external/
│   ├── openMINDS_JSON-Schema/     # openMINDS schemas (submodule)
│   └── openMINDS_instances/       # Controlled term instances (submodule)
├── output/demo/                   # Generated elements
├── main.py                        # CLI entry point
├── config.yaml                    # Configuration
└── README.md
```

## Configuration

Edit `config.yaml`:

```yaml
openminds:
  submodule_path: "external/openMINDS_JSON-Schema"
  version: "latest"

cedar:
  api:
    base_url: "https://resource.metadatacenter.org"
  folder_id: "https://repo.metadatacenter.org/folders/YOUR-FOLDER-ID"
```

## How It Works

1. **Schema Loading**: Loads openMINDS JSON Schema from submodule
2. **Controlled Terms Detection**: Automatically detects fields with controlled vocabularies
3. **Field Generation**: Creates CEDAR fields with appropriate inputType
   - Radio buttons (<=5 options): biologicalSex (4 options)
   - Dropdown list (>5 options): species (25 options)
4. **Value Constraints**: Generates CEDAR literals from openMINDS instances
5. **Validation**: Validates against CEDAR schema
6. **Upload**: Uploads to CEDAR Workbench via REST API

## Key Design Decisions

### List/Radio vs Ontology References

Uses list/radio inputTypes with literals from openMINDS instances for:
- User-friendly dropdown and radio button UI
- Exact control over selectable terms
- Full CEDAR validation compliance

Trade-off: Semantic IRIs not directly preserved in UI (see NEXT_STEPS.md)

### Field Structure

- **Literal fields** (list, radio, checkbox): Use `@value` property
- **Link fields** (controlled-term, link): Use `@id` property

### URL Extraction

openMINDS uses full URLs as property keys. Converter extracts clean field names:
- Input: `https://openminds.om-i.org/props/biologicalSex`
- Output: `biologicalSex`

Semantic URLs preserved in `@context` for JSON-LD compatibility.

## Testing

```bash
# Generate element
python tests/test_generation.py

# Validate
python tests/test_validation.py

# View comprehensive demo
quarto render notebooks/demo.qmd
```

## Documentation

- **notebooks/demo.qmd**: Comprehensive demo with all features
- **NEXT_STEPS.md**: Roadmap for semantic robustness

## Examples

### Subject Schema Conversion

Input: openMINDS Subject schema

Output: CEDAR TemplateElement with:
- 6 fields total
- 2 controlled term fields
  - biologicalSex: Radio buttons (4 options)
  - species: Dropdown list (25 options)

### Controlled Terms Coverage

- 81 controlled term types available
- 2,700+ instances across all types
- Automatically applied to any schema

## Requirements

- Python 3.8+
- Dependencies: pyyaml, requests, python-dotenv
- Quarto (for demo rendering)
- CEDAR API key (for upload)

## Limitations

- Semantic IRIs not preserved in field values
- No direct ontology integration (BioPortal/PATO)
- Static term lists (no dynamic updates)
- No custom vocabulary mappings

See NEXT_STEPS.md for enhancement roadmap.

## License

MIT License

## Support

- GitHub Issues: [repository]/issues
- CEDAR Documentation: https://metadatacenter.readthedocs.io
- openMINDS Documentation: https://openminds-documentation.readthedocs.io
