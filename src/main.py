#!/usr/bin/env python3
"""
openMINDS to CEDAR Element Converter - Main CLI
================================================

Main command-line interface for the converter with CEDAR API integration.

Usage:
    python src/main.py load             # Load schemas from submodule
    python src/main.py convert          # Convert schemas to CEDAR elements
    python src/main.py upload           # Upload elements to CEDAR Workbench
    python src/main.py all              # Load, convert, and upload
    python src/main.py single <schema>  # Convert single schema

Author: Metadata Harmonization Project
License: MIT
"""

import sys
import os
import argparse
import logging
from pathlib import Path
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from schema_loader import OpenMINDSSchemaLoader
from batch_converter import BatchConverter
from cedar_api import CEDARAPIClient, upload_elements_from_directory


# Load environment variables
load_dotenv()

# Setup logging
def setup_logging(verbose: bool = False):
    """Configure logging"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

logger = logging.getLogger(__name__)


def load_schemas(args):
    """Load openMINDS schemas from git submodule"""
    print("\\n" + "="*60)
    print("LOADING OPENMINDS SCHEMAS FROM SUBMODULE")
    print("="*60 + "\\n")

    try:
        loader = OpenMINDSSchemaLoader(args.config)

        # Verify submodule
        print("Verifying submodule...")
        verification = loader.verify_submodule()

        if not verification['submodule_exists']:
            print("✗ Submodule not found!")
            print("\\nPlease initialize the submodule:")
            print("  git submodule update --init --recursive")
            return False

        print(f"✓ Submodule path: {loader.submodule_path}")
        print(f"✓ Version: {verification['version']}")
        print(f"✓ Available versions: {', '.join(verification['available_versions'])}")
        print(f"✓ Categories: {', '.join(verification['categories'])}")
        print()

        # Load schemas
        schemas = loader.load_all_configured_schemas()

        if schemas:
            print(f"\\n✓ Successfully loaded {len(schemas)} schemas")
            print(f"\\nSchemas by category:")

            # Group by category
            categories = {}
            for schema_id in schemas.keys():
                parts = schema_id.split('/')
                category = '/'.join(parts[:2])
                categories[category] = categories.get(category, 0) + 1

            for category, count in sorted(categories.items()):
                print(f"  {category}: {count} schemas")

            return True
        else:
            print(f"\\n✗ No schemas loaded")
            return False

    except Exception as e:
        print(f"\\n✗ Error: {e}")
        logger.exception("Failed to load schemas")
        return False


def convert_schemas(args):
    """Convert openMINDS schemas to CEDAR elements"""
    print("\\n" + "="*60)
    print("CONVERTING SCHEMAS TO CEDAR ELEMENTS")
    print("="*60 + "\\n")

    try:
        # Load schemas
        loader = OpenMINDSSchemaLoader(args.config)
        schemas = loader.load_all_configured_schemas()

        if not schemas:
            print("No schemas to convert")
            return False

        # Convert
        converter = BatchConverter(
            output_dir=args.output_dir,
            config_path=args.config
        )

        elements = converter.convert_schemas_from_dict(schemas)

        if elements:
            print(f"\\n✓ Successfully converted {len(elements)} schemas")
            print(f"✓ Saved to: {args.output_dir}")
            return True
        else:
            print(f"\\n✗ No schemas converted")
            return False

    except Exception as e:
        print(f"\\n✗ Error: {e}")
        logger.exception("Failed to convert schemas")
        return False


def upload_elements(args):
    """Upload CEDAR elements to CEDAR Workbench"""
    print("\\n" + "="*60)
    print("UPLOADING ELEMENTS TO CEDAR WORKBENCH")
    print("="*60 + "\\n")

    try:
        # Check for API key
        if not os.getenv("CEDAR_API_KEY"):
            print("✗ CEDAR_API_KEY not set")
            print("\\nPlease set your CEDAR API key:")
            print("  export CEDAR_API_KEY='your-api-key-here'")
            print("\\nGet your API key from: https://cedar.metadatacenter.org/profile")
            return False

        # Initialize API client
        client = CEDARAPIClient(config_path=args.config)

        # Validate connection
        print("Validating CEDAR API connection...")
        client.validate_connection()
        print("✓ Connection validated\\n")

        # Upload
        result = upload_elements_from_directory(
            directory=args.output_dir,
            config_path=args.config,
            folder_id=args.folder_id,
            pattern="*_element.json"
        )

        print(f"\\n{'='*60}")
        print("UPLOAD SUMMARY")
        print(f"{'='*60}")
        print(f"Total elements: {result['total']}")
        print(f"Successful: {result['successful']}")
        print(f"Failed: {result['failed']}")

        if result['successful'] > 0:
            print(f"\\nSuccessfully uploaded elements:")
            for r in result['results']:
                if r['status'] == 'success':
                    print(f"  ✓ {r['element_name']}")
                    print(f"    CEDAR ID: {r['cedar_id']}")

        if result['failed'] > 0:
            print(f"\\nFailed uploads:")
            for r in result['results']:
                if r['status'] == 'failed':
                    print(f"  ✗ {r['element_name']}: {r.get('error', 'Unknown error')}")

        print(f"\\n{'='*60}\\n")

        return result['successful'] > 0

    except Exception as e:
        print(f"\\n✗ Error: {e}")
        logger.exception("Failed to upload elements")
        return False


def convert_single(args):
    """Convert a single schema"""
    print("\\n" + "="*60)
    print("CONVERTING SINGLE SCHEMA")
    print("="*60 + "\\n")

    try:
        # Parse schema identifier: category/subcategory/filename
        parts = args.schema.split('/')

        if len(parts) == 3:
            category, subcategory, filename = parts
        elif len(parts) == 1:
            # Assume core/research by default
            category = "core"
            subcategory = "research"
            filename = parts[0]
        else:
            print(f"✗ Invalid schema identifier: {args.schema}")
            print("\\nExpected format: category/subcategory/filename")
            print("Example: core/research/subject.schema.json")
            print("Or just: subject.schema.json (assumes core/research)")
            return False

        # Load schema
        loader = OpenMINDSSchemaLoader(args.config)
        schema = loader.load_schema(category, subcategory, filename)

        print(f"✓ Loaded schema: {category}/{subcategory}/{filename}")
        print()

        # Convert
        converter = BatchConverter(
            output_dir=args.output_dir,
            config_path=args.config
        )

        schema_id = f"{category}/{subcategory}/{filename}"
        element = converter.convert_schema_dict(schema, schema_id, args.name)

        if element:
            print(f"\\n✓ Successfully converted {filename}")

            if args.upload:
                print("\\nUploading to CEDAR...")
                client = CEDARAPIClient(config_path=args.config)
                response = client.upload_element(element, args.folder_id)
                print(f"✓ Uploaded: {response.get('@id')}")

            return True
        else:
            print(f"\\n✗ Failed to convert {filename}")
            return False

    except Exception as e:
        print(f"\\n✗ Error: {e}")
        logger.exception("Failed to convert single schema")
        return False


def run_all(args):
    """Run complete workflow: load, convert, and optionally upload"""
    print("\\n" + "="*60)
    print("COMPLETE WORKFLOW: LOAD → CONVERT → UPLOAD")
    print("="*60 + "\\n")

    # Load schemas
    if not load_schemas(args):
        return False

    print("\\n" + "-"*60)
    print("Proceeding to conversion...")
    print("-"*60 + "\\n")

    # Convert schemas
    if not convert_schemas(args):
        return False

    # Upload if requested
    if args.upload:
        print("\\n" + "-"*60)
        print("Proceeding to upload...")
        print("-"*60 + "\\n")

        return upload_elements(args)

    return True


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Convert openMINDS schemas to CEDAR elements",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Complete workflow (load, convert, upload)
  python src/main.py all --upload

  # Load schemas from submodule
  python src/main.py load

  # Convert schemas to CEDAR elements
  python src/main.py convert

  # Upload elements to CEDAR
  python src/main.py upload

  # Convert single schema
  python src/main.py single subject.schema.json --name Subject
  python src/main.py single core/research/subject.schema.json

  # Use custom output directory
  python src/main.py convert --output-dir my_output

Environment Variables:
  CEDAR_API_KEY    Your CEDAR Workbench API key (required for upload)

Configuration:
  Edit config.yaml to customize schemas, ontology mappings, and CEDAR settings
        """
    )

    parser.add_argument(
        '--config',
        default='config.yaml',
        help='Configuration file (default: config.yaml)'
    )

    parser.add_argument(
        '--output-dir',
        default='output/cedar_elements',
        help='Output directory for CEDAR elements (default: output/cedar_elements)'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Verbose output'
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    # Load command
    load_parser = subparsers.add_parser(
        'load',
        help='Load openMINDS schemas from git submodule'
    )

    # Convert command
    convert_parser = subparsers.add_parser(
        'convert',
        help='Convert openMINDS schemas to CEDAR elements'
    )

    # Upload command
    upload_parser = subparsers.add_parser(
        'upload',
        help='Upload CEDAR elements to CEDAR Workbench'
    )
    upload_parser.add_argument(
        '--folder-id',
        help='CEDAR folder ID (overrides config)'
    )

    # All command
    all_parser = subparsers.add_parser(
        'all',
        help='Run complete workflow (load + convert + upload)'
    )
    all_parser.add_argument(
        '--upload',
        action='store_true',
        help='Upload to CEDAR after conversion'
    )
    all_parser.add_argument(
        '--folder-id',
        help='CEDAR folder ID (overrides config)'
    )

    # Single command
    single_parser = subparsers.add_parser(
        'single',
        help='Convert a single schema'
    )
    single_parser.add_argument(
        'schema',
        help='Schema identifier (e.g., subject.schema.json or core/research/subject.schema.json)'
    )
    single_parser.add_argument(
        '--name',
        help='Custom element name'
    )
    single_parser.add_argument(
        '--upload',
        action='store_true',
        help='Upload to CEDAR after conversion'
    )
    single_parser.add_argument(
        '--folder-id',
        help='CEDAR folder ID (overrides config)'
    )

    args = parser.parse_args()

    # Setup logging
    setup_logging(args.verbose)

    if not args.command:
        parser.print_help()
        return 1

    # Execute command
    try:
        if args.command == 'load':
            success = load_schemas(args)
        elif args.command == 'convert':
            success = convert_schemas(args)
        elif args.command == 'upload':
            success = upload_elements(args)
        elif args.command == 'all':
            success = run_all(args)
        elif args.command == 'single':
            success = convert_single(args)
        else:
            parser.print_help()
            return 1

        return 0 if success else 1

    except KeyboardInterrupt:
        print("\\n\\nInterrupted by user")
        return 130
    except Exception as e:
        logger.exception("Unexpected error")
        print(f"\\n✗ Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
