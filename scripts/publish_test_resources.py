#!/usr/bin/env python
"""Helper script to clear and repopulate CEDAR test folder with all registry resources.

Usage:
    uv run python scripts/publish_test_resources.py

This script:
1. Clears all resources from CEDAR test folders
2. Generates and uploads ALL elements from registry (organized by module)
3. Generates and uploads ALL templates from registry
4. Saves generated resources locally with folder structure
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, ".")

from openminds2cedar.generators import CEDARElementGenerator, CEDARTemplateGenerator
from openminds2cedar.registry import Registry
from openminds2cedar.api import CEDARClient


def main():
    client = CEDARClient()
    registry = Registry()
    element_gen = CEDARElementGenerator(registry=registry)
    template_gen = CEDARTemplateGenerator()

    output_dir = Path("output")

    # =========================================================================
    # Step 1: Clear all resources
    # =========================================================================
    print("=" * 60)
    print("Step 1: Clearing CEDAR folders")
    print("=" * 60)
    client.clear_all()
    print()

    # =========================================================================
    # Step 2: Generate and upload ALL elements from registry (organized by module)
    # =========================================================================
    print("=" * 60)
    print("Step 2: Generating and Uploading Elements")
    print("=" * 60)

    schemas = registry.schemas
    print(f"Found {len(schemas)} schemas in registry\n")

    # Group schemas by module
    schemas_by_module = {}
    for schema in schemas:
        module, name = schema.split(".")
        schemas_by_module.setdefault(module, []).append(schema)

    # Create subfolders on CEDAR for each module
    print("Creating subfolders on CEDAR...")
    module_folders = {}
    elements_parent = client.folders["elements"]
    for module in schemas_by_module.keys():
        folder_id = client.get_or_create_subfolder(module, elements_parent)
        if folder_id:
            module_folders[module] = folder_id
            print(f"  + {module}/")
        else:
            print(f"  ! Failed to create folder: {module}/")
    print()

    success_count = 0
    fail_count = 0
    uploaded_elements = {}

    for schema in schemas:
        module, name = schema.split(".")
        try:
            # Generate element
            element = element_gen.generate(schema)

            # Save locally (organized by module)
            element_dir = output_dir / "elements" / module
            element_dir.mkdir(parents=True, exist_ok=True)
            element_path = element_dir / f"{name.lower()}.json"
            with open(element_path, "w") as f:
                json.dump(element, f, indent=2)

            # Upload to CEDAR (in module subfolder)
            target_folder = module_folders.get(module, elements_parent)
            result = client.upload(element, "element", folder_id=target_folder)
            if result["success"]:
                print(f"  + {schema}")
                success_count += 1
            else:
                print(f"  ! {schema}: {result['error'][:80]}")
                fail_count += 1

        except Exception as e:
            print(f"  ! {schema}: {str(e)[:80]}")
            fail_count += 1

    print(f"\nElements: {success_count} uploaded, {fail_count} failed\n")

    # Fetch uploaded elements with real IDs (from all module subfolders)
    print("Fetching uploaded elements with real IDs...")
    for folder_id in module_folders.values():
        for item in client.list_folder(folder_id):
            element = client.get_element(item["@id"])
            if element:
                name = element.get("schema:name")
                uploaded_elements[name] = element
    print(f"  Retrieved {len(uploaded_elements)} elements\n")

    # =========================================================================
    # Step 3: Generate and upload ALL templates from registry
    # =========================================================================
    print("=" * 60)
    print("Step 3: Generating and Uploading Templates")
    print("=" * 60)

    template_names = registry.templates
    print(f"Found {len(template_names)} templates in registry\n")

    template_success = 0
    template_fail = 0

    for template_name in template_names:
        try:
            template_def = registry.template(template_name)

            # Collect elements and cardinalities for this template
            elements = []
            element_ids = []
            cardinalities = []

            for elem_def in template_def["elements"]:
                schema_path = elem_def["schema"]
                module, schema_name = schema_path.split(".")
                element_key = schema_name.lower()

                if element_key not in uploaded_elements:
                    print(f"  ! {template_name}: Missing element '{element_key}'")
                    continue

                element = uploaded_elements[element_key]
                elements.append(element)
                element_ids.append(element["@id"])
                cardinalities.append(elem_def.get("multiple", False))

            if len(elements) != len(template_def["elements"]):
                template_fail += 1
                continue

            # Generate template
            # Use registry key as schema:name (for lookup), display name in description
            display_name = template_def.get("name", template_name)
            description = template_def.get("description", "")
            if display_name != template_name:
                description = f"{display_name}: {description}"

            template = template_gen.generate(
                elements=elements,
                element_ids=element_ids,
                name=template_name,  # Registry key for consistent lookup
                description=description,
                cardinalities=cardinalities,
            )

            # Save locally
            template_dir = output_dir / "templates"
            template_dir.mkdir(parents=True, exist_ok=True)
            template_path = template_dir / f"{template_name}.json"
            with open(template_path, "w") as f:
                json.dump(template, f, indent=2)

            # Upload to CEDAR
            result = client.upload_template(template)
            if result["success"]:
                print(f"  + {template_name}")
                template_success += 1
            else:
                print(f"  ! {template_name}: {result['error'][:80]}")
                template_fail += 1

        except Exception as e:
            print(f"  ! {template_name}: {str(e)[:80]}")
            template_fail += 1

    print(f"\nTemplates: {template_success} uploaded, {template_fail} failed\n")

    # =========================================================================
    # Summary
    # =========================================================================
    print("=" * 60)
    print("Summary")
    print("=" * 60)

    tmpl_count = len(list(client.list_folder(client.folders["templates"])))

    print(f"Elements:   {success_count} on CEDAR (organized in {len(module_folders)} module folders)")
    print(f"Templates:  {tmpl_count} on CEDAR")
    print(f"\nLocal output: {output_dir}/")
    print(f"  elements/  - {success_count} files (organized by module)")
    print(f"  templates/ - {template_success} files")

    print()
    print("Resource URLs:")
    print("-" * 60)

    print("\nElement Folders:")
    for module, folder_id in sorted(module_folders.items()):
        count = len(list(client.list_folder(folder_id)))
        print(f"  {module}/ ({count} elements): {folder_id}")

    print("\nTemplates:")
    for item in client.list_folder(client.folders["templates"]):
        print(f"  {item.get('schema:name')}: {item['@id']}")

    # =========================================================================
    # Step 4: Download published resources (with real CEDAR IDs)
    # =========================================================================
    print()
    print("=" * 60)
    print("Step 4: Downloading from CEDAR")
    print("=" * 60)
    client.download_all(output_dir)

    return fail_count == 0 and template_fail == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
