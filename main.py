#!/usr/bin/env python3
"""
openMINDS to CEDAR Converter - Main Entry Point

Convert openMINDS schemas to CEDAR elements and upload to CEDAR Workbench.
"""

import sys
import argparse
import yaml
from pathlib import Path

sys.path.insert(0, 'src')

from src.schema_loader import OpenMINDSSchemaLoader
from src.cedar_element_generator import CEDARElementGenerator
from src.cedar_api import CEDARAPIClient


def load_config(config_path="config.yaml"):
    """Load configuration file"""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def process_schema(loader, generator, category, subcategory, schema_file, output_dir):
    """Process a single schema file"""
    try:
        # Load schema
        schema = loader.load_schema(category, subcategory, schema_file)

        # Generate element name from schema file
        element_name = schema_file.replace('.schema.json', '').title()

        # Generate CEDAR element
        element = generator.create_element_from_openminds(schema, element_name)

        # Save to output directory
        output_file = output_dir / f"{schema_file.replace('.schema.json', '')}_element.json"
        generator.save_element(element, str(output_file))

        print(f"✓ Generated: {element_name} -> {output_file}")
        return element, output_file

    except Exception as e:
        print(f"✗ Failed to process {schema_file}: {e}")
        return None, None


def generate_all(config_path="config.yaml"):
    """Generate CEDAR elements from all schemas in config"""
    config = load_config(config_path)

    # Initialize components
    loader = OpenMINDSSchemaLoader(config_path)
    generator = CEDARElementGenerator()

    # Setup output directory
    output_dir = Path(config['directories']['output'])
    output_dir.mkdir(parents=True, exist_ok=True)

    results = []

    # Process schemas by category
    schemas_config = config['openminds']['schemas']

    for category, subcategories in schemas_config.items():
        if not subcategories:
            continue

        print(f"\nProcessing category: {category}")
        print("-" * 60)

        for subcategory, schema_files in subcategories.items():
            if not schema_files:
                continue

            print(f"\n  Subcategory: {subcategory}")

            for schema_file in schema_files:
                element, output_file = process_schema(
                    loader, generator, category, subcategory,
                    schema_file, output_dir
                )
                if element and output_file:
                    results.append((element, output_file))

    print(f"\n{'='*60}")
    print(f"Generated {len(results)} CEDAR elements")
    print(f"Output directory: {output_dir}")

    return results


def validate_all(elements=None, config_path="config.yaml"):
    """Validate generated CEDAR elements"""
    try:
        client = CEDARAPIClient(config_path)
    except ValueError as e:
        print(f"✗ Cannot validate: {e}")
        return

    if elements is None:
        # Load from output directory
        config = load_config(config_path)
        output_dir = Path(config['directories']['output'])
        element_files = list(output_dir.glob("*_element.json"))

        print(f"Found {len(element_files)} elements to validate")

        for element_file in element_files:
            try:
                import json
                with open(element_file) as f:
                    element = json.load(f)

                result = client.validate_element(element)
                validates = result.get("validates", False)

                if validates:
                    print(f"✓ Valid: {element_file.name}")
                else:
                    print(f"✗ Invalid: {element_file.name}")
                    if "errors" in result:
                        for error in result["errors"][:3]:
                            print(f"  - {error}")
            except Exception as e:
                print(f"✗ Error validating {element_file.name}: {e}")
    else:
        # Validate provided elements
        for element, _ in elements:
            try:
                result = client.validate_element(element)
                validates = result.get("validates", False)
                element_name = element.get("schema:name", "unknown")

                if validates:
                    print(f"✓ Valid: {element_name}")
                else:
                    print(f"✗ Invalid: {element_name}")
            except Exception as e:
                print(f"✗ Error validating: {e}")


def upload_all(elements=None, config_path="config.yaml"):
    """Upload generated CEDAR elements to CEDAR Workbench"""
    try:
        client = CEDARAPIClient(config_path)
    except ValueError as e:
        print(f"✗ Cannot upload: {e}")
        return

    if elements is None:
        # Load from output directory
        config = load_config(config_path)
        output_dir = Path(config['directories']['output'])
        element_files = list(output_dir.glob("*_element.json"))

        print(f"Found {len(element_files)} elements to upload")

        uploaded = 0
        for element_file in element_files:
            try:
                response = client.upload_element_from_file(str(element_file))
                print(f"✓ Uploaded: {element_file.name} -> {response.get('@id')}")
                uploaded += 1
            except Exception as e:
                print(f"✗ Failed to upload {element_file.name}: {e}")

        print(f"\n{'='*60}")
        print(f"Uploaded {uploaded}/{len(element_files)} elements")
    else:
        # Upload provided elements
        uploaded = 0
        for element, _ in elements:
            try:
                response = client.upload_element(element)
                element_name = element.get("schema:name", "unknown")
                print(f"✓ Uploaded: {element_name} -> {response.get('@id')}")
                uploaded += 1
            except Exception as e:
                print(f"✗ Failed to upload: {e}")

        print(f"\n{'='*60}")
        print(f"Uploaded {uploaded}/{len(elements)} elements")


def main():
    parser = argparse.ArgumentParser(
        description="Convert openMINDS schemas to CEDAR elements"
    )
    parser.add_argument(
        'command',
        choices=['generate', 'validate', 'upload', 'all'],
        help='Command to execute'
    )
    parser.add_argument(
        '--config',
        default='config.yaml',
        help='Path to config file (default: config.yaml)'
    )

    args = parser.parse_args()

    if args.command == 'generate':
        print("Generating CEDAR elements from openMINDS schemas...")
        print("="*60)
        elements = generate_all(args.config)

    elif args.command == 'validate':
        print("Validating CEDAR elements...")
        print("="*60)
        validate_all(config_path=args.config)

    elif args.command == 'upload':
        print("Uploading CEDAR elements to CEDAR Workbench...")
        print("="*60)
        upload_all(config_path=args.config)

    elif args.command == 'all':
        print("Running complete workflow...")
        print("="*60)

        # Generate
        print("\n1. GENERATING ELEMENTS")
        print("="*60)
        elements = generate_all(args.config)

        # Validate
        print("\n2. VALIDATING ELEMENTS")
        print("="*60)
        validate_all(elements, args.config)

        # Upload
        print("\n3. UPLOADING ELEMENTS")
        print("="*60)
        upload_all(elements, args.config)

        print("\n✓ Workflow complete!")


if __name__ == "__main__":
    main()
