# openMINDS to CEDAR Converter

Converts openMINDS metadata schemas to CEDAR TemplateElements with automatic controlled vocabulary integration.

## Setup

```bash
git clone https://github.com/openMetadataInitiative/openminds2cedar.git
cd openminds2cedar
git submodule update --init --recursive
conda env create -f environment.yml
conda activate openminds2cedar
echo "CEDAR_API_KEY=your-key" > .env
```

## Usage

```bash
# Generate CEDAR element
python main.py generate

# Validate and upload
python main.py validate
python main.py upload
```

## Features

- Converts openMINDS schemas to CEDAR format
- Integrates controlled vocabularies
- Smart UI selection (radio buttons for small lists, dropdowns for large)
- CEDAR API validation and upload

## Configuration

Edit `config.yaml` to set your openMINDS schema path and CEDAR folder ID.

## Project Structure

- `src/` - Core conversion logic
- `tests/` - Test files
- `notebooks/demo.qmd` - Comprehensive demo
- `external/` - openMINDS submodules
- `output/` - Generated elements
- `config.yaml` - Configuration file
