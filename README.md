# openMINDS to CEDAR Element Converter

Convert [openMINDS](https://github.com/openMetadataInitiative/openMINDS_JSON-Schema) metadata schemas to [CEDAR Workbench](https://cedar.metadatacenter.org/) reusable elements automatically, with direct API integration for uploading to CEDAR.

## Overview

This tool programmatically converts openMINDS JSON schemas into CEDAR Elements that can be:
- Uploaded directly to CEDAR Workbench via API
- Edited using the CEDAR metadata editor
- Reused across multiple CEDAR templates
- Integrated with ontologies (PATO, NCBITAXON, etc.)

## Features

- **Git submodule integration** - Uses openMINDS_JSON-Schema as submodule (no manual downloads)
- **CEDAR API integration** - Direct upload to CEDAR Workbench
- **Configurable schema selection** - Choose which schemas to convert via config.yaml
- **Batch conversion** - Convert multiple schemas at once
- **Ontology mapping** - Automatic mapping to biomedical ontologies
- **Field type detection** - Smart conversion of text, numeric, and controlled term fields
- **Validation-ready output** - CEDAR-compliant elements
- **Detailed reporting** - Conversion and upload statistics

## Quick Start

### 1. Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd openminds2cedar

# Initialize submodule and install dependencies
./quickstart.sh
```

The quickstart script will:
- Install Python dependencies
- Initialize the openMINDS_JSON-Schema submodule
- Load schemas from the submodule
- Convert them to CEDAR elements

Output will be in: `output/cedar_elements/`

### 2. Upload to CEDAR (Optional)

```bash
# Get your API key from https://cedar.metadatacenter.org/profile
export CEDAR_API_KEY='your-api-key-here'

# Upload all elements
python src/main.py upload
```

## Installation

### Prerequisites

- Python 3.7+
- Git
- CEDAR Workbench account (for upload features)

### Setup

```bash
# Clone repository
git clone <repository-url>
cd openminds2cedar

# Initialize git submodule
git submodule update --init --recursive

# Install core dependencies
pip install requests pyyaml python-dotenv

# Or install all dependencies (including optional)
pip install -r requirements.txt
```

### Configuration

1. **Edit `config.yaml`** to select which schemas to convert:

```yaml
openminds:
  version: "latest"  # or v4.0, v3.0, etc.
  schemas:
    core:
      research:
        - subject.schema.json
        - subjectState.schema.json
      actors:
        - person.schema.json
        - organization.schema.json
```

2. **Set up CEDAR API key** (for upload features):

```bash
# Copy the example file
cp .env.example .env

# Edit .env and add your CEDAR API key
# CEDAR_API_KEY=your-api-key-here
```

Get your API key from: https://cedar.metadatacenter.org/profile

## Usage

### Command Line Interface

The CLI provides five main commands:

#### 1. Load Schemas

Load and verify schemas from the submodule:

```bash
python src/main.py load
```

#### 2. Convert Schemas

Convert schemas to CEDAR elements:

```bash
python src/main.py convert
```

Output: `output/cedar_elements/*.json`

#### 3. Upload to CEDAR

Upload generated elements to CEDAR Workbench:

```bash
# Set API key first
export CEDAR_API_KEY='your-key'

# Upload
python src/main.py upload
```

Optional: Specify target folder:
```bash
python src/main.py upload --folder-id https://repo.metadatacenter.org/folders/...
```

#### 4. Complete Workflow

Run all steps at once:

```bash
# Load + Convert + Upload
python src/main.py all --upload

# Load + Convert only (no upload)
python src/main.py all
```

#### 5. Convert Single Schema

Convert a specific schema:

```bash
# By filename (assumes core/research)
python src/main.py single subject.schema.json --name Subject

# With full path
python src/main.py single core/research/subject.schema.json

# Convert and upload immediately
python src/main.py single subject.schema.json --upload
```

### Python API

Use the converter directly in your code:

```python
from src.schema_loader import OpenMINDSSchemaLoader
from src.batch_converter import BatchConverter
from src.cedar_api import CEDARAPIClient

# Load schemas
loader = OpenMINDSSchemaLoader()
schemas = loader.load_all_configured_schemas()
print(f"Loaded {len(schemas)} schemas")

# Convert to CEDAR elements
converter = BatchConverter()
elements = converter.convert_schemas_from_dict(schemas)
print(f"Converted {len(elements)} elements")

# Upload to CEDAR
client = CEDARAPIClient()
for element in elements:
    response = client.upload_element(element)
    print(f"Uploaded: {response['@id']}")
```

## Project Structure

```
openminds2cedar/
├── src/                              # Source code
│   ├── main.py                       # CLI interface
│   ├── schema_loader.py              # Load schemas from submodule
│   ├── batch_converter.py            # Batch conversion
│   ├── cedar_element_generator.py    # Core converter
│   └── cedar_api.py                  # CEDAR API client
│
├── external/
│   └── openMINDS_JSON-Schema/        # Git submodule (schemas)
│
├── output/
│   ├── cedar_elements/               # Generated elements
│   └── backups/                      # Backups before upload
│
├── docs/                             # Documentation
│   ├── ARCHITECTURE.md               # System design
│   ├── API_REFERENCE.md              # API documentation
│   └── FIELD_MAPPING.md              # Field type mappings
│
├── examples/                         # Example files
├── tests/                            # Test files
├── config.yaml                       # Main configuration
├── .env.example                      # Environment variables template
├── requirements.txt                  # Python dependencies
└── README.md                         # This file
```

## Configuration

### config.yaml

Main configuration file for:

- **Schema selection**: Which openMINDS schemas to convert
- **CEDAR API settings**: Base URL, timeout, folder ID
- **Ontology mappings**: Custom field-to-ontology mappings
- **Conversion options**: Naming conventions, error handling

Example:

```yaml
cedar:
  version: "1.6.0"
  api:
    base_url: "https://resource.metadatacenter.org"
    folder_id: null  # Or your folder URL

openminds:
  submodule_path: "external/openMINDS_JSON-Schema"
  version: "latest"
  schemas:
    core:
      research:
        - subject.schema.json
        - subjectState.schema.json
      actors:
        - person.schema.json

ontology_mappings:
  biologicalSex:
    acronym: "PATO"
    uri: "http://purl.obolibrary.org/obo/PATO_0000047"
  species:
    acronym: "NCBITAXON"
    uri: "https://data.bioontology.org/ontologies/NCBITAXON"
```

### Environment Variables

Create a `.env` file (see `.env.example`):

```bash
# Required for upload features
CEDAR_API_KEY=your-api-key-here

# Optional overrides
CEDAR_BASE_URL=https://resource.metadatacenter.org
CEDAR_FOLDER_ID=https://repo.metadatacenter.org/folders/...
```

## Field Type Mapping

The converter automatically maps openMINDS field types to CEDAR:

| openMINDS Type | CEDAR Field Type | CEDAR Input Type | Example |
|----------------|------------------|------------------|---------|
| `string` | TemplateField | textfield | name, description |
| `number`, `integer` | TemplateField | numeric | age, weight |
| `_linkedTypes: ["BiologicalSex"]` | TemplateField | textfield + PATO ontology | biologicalSex |
| `_linkedTypes: ["Species"]` | TemplateField | textfield + NCBITAXON ontology | species |
| `array` + IRI items | TemplateField | textfield (multipleChoice) | authors, keywords |

For detailed mapping rules, see [docs/FIELD_MAPPING.md](docs/FIELD_MAPPING.md).

## CEDAR API Integration

### Getting Your API Key

1. Log in to [CEDAR Workbench](https://cedar.metadatacenter.org/)
2. Go to your profile (click your name → Profile)
3. Click "Show API Key"
4. Copy the key

### Finding Your Folder ID

1. In CEDAR Workbench, navigate to the folder where you want to upload
2. Copy the folder URL from the browser
3. Extract the folder ID from the URL:
   ```
   https://cedar.metadatacenter.org/dashboard?folderId=https:%2F%2Frepo.metadatacenter.org%2Ffolders%2F...
                                                        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                                                        This is your folder ID (URL-encoded)
   ```
4. Add to `config.yaml` or use `--folder-id` flag

### Upload Options

```bash
# Upload to default workspace root
python src/main.py upload

# Upload to specific folder
python src/main.py upload --folder-id https://repo.metadatacenter.org/folders/your-folder-id

# Upload with verbose logging
python src/main.py upload -v
```

## Examples

### Example 1: Convert All Configured Schemas

```bash
# Edit config.yaml to select schemas
python src/main.py convert

# Check output
ls output/cedar_elements/
cat output/cedar_elements/conversion_report.json
```

### Example 2: Convert and Upload

```bash
# Set API key
export CEDAR_API_KEY='your-key'

# Run complete workflow
python src/main.py all --upload
```

### Example 3: Convert Specific Schema

```bash
# Convert subject schema
python src/main.py single subject.schema.json --name "Subject Element"

# Convert and upload immediately
python src/main.py single subject.schema.json --upload --folder-id https://repo.metadatacenter.org/folders/...
```

### Example 4: Update Submodule to Latest

```bash
# Update openMINDS schemas to latest version
git submodule update --remote

# Re-convert with new schemas
python src/main.py convert
```

## Interactive Demo

Explore the Jupyter notebook for interactive demonstration:

```bash
jupyter notebook cedar_element_demo.ipynb
```

The notebook includes:
- Step-by-step conversion walkthrough
- Element structure inspection
- Field comparison tables
- Upload examples

## Troubleshooting

### "Submodule not found"

```bash
# Initialize the submodule
git submodule update --init --recursive
```

### "CEDAR_API_KEY not set"

```bash
# Set the environment variable
export CEDAR_API_KEY='your-api-key-here'

# Or add to .env file
echo "CEDAR_API_KEY=your-key" > .env
```

### "Failed to load schema"

Check that:
1. Submodule is initialized: `ls external/openMINDS_JSON-Schema`
2. Schema exists in config.yaml
3. Schema version is correct (latest, v4.0, etc.)

### "Upload failed with 401"

Your API key is invalid or expired. Get a new key from CEDAR profile.

### "Upload failed with 403"

You don't have permission to write to the specified folder. Check folder ID or use default workspace.

## Development

### Running Tests

```bash
pytest tests/
```

### Code Formatting

```bash
black src/
```

### Type Checking

```bash
mypy src/
```

### Adding New Schemas

1. Edit `config.yaml`:
```yaml
openminds:
  schemas:
    core:
      your_category:
        - your_schema.schema.json
```

2. Run conversion:
```bash
python src/main.py convert
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License - See [LICENSE](LICENSE) for details.

## References

- [openMINDS_JSON-Schema](https://github.com/openMetadataInitiative/openMINDS_JSON-Schema) - Source schemas
- [CEDAR Workbench](https://cedar.metadatacenter.org/) - Metadata authoring platform
- [CEDAR API Documentation](https://metadatacenter.github.io/cedar-manual/) - API reference

## Authors

Metadata Harmonization Project

## Support

For issues and questions:
- Open an issue on GitHub
- Check the [troubleshooting section](#troubleshooting)
- Review the [documentation](docs/)
- Try the [interactive demo](cedar_element_demo.ipynb)

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history.
