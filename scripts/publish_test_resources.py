#!/usr/bin/env python
"""Helper script to clear and repopulate CEDAR test folder, then validate conversion.

Usage:
    uv run python scripts/publish_test_resources.py

This script:
1. Clears all resources from CEDAR test folders
2. Generates and uploads elements (Subject, SubjectState, etc.)
3. Generates and uploads templates
4. Uploads test instances using shared fixtures from tests/fixtures
5. Downloads and converts instances to openMINDS
6. Validates converted objects using openMINDS validator
"""

import sys
sys.path.insert(0, ".")  # Allow importing from tests/fixtures

from openminds2cedar.generators import CEDARElementGenerator, CEDARTemplateGenerator, CEDARInstanceGenerator
from openminds2cedar.registry import Registry
from openminds2cedar.api import CEDARClient
from openminds2cedar.converters import CEDARToOpenMINDSConverter

# Import shared fixtures (single source of truth)
from tests.fixtures import MOCK_SUBJECT_DATA, MOCK_SUBJECTSTATE_DATA


def main():
    client = CEDARClient()
    registry = Registry()
    element_gen = CEDARElementGenerator(registry=registry)
    template_gen = CEDARTemplateGenerator()
    converter = CEDARToOpenMINDSConverter()

    # =========================================================================
    # Step 1: Clear all resources
    # =========================================================================
    print("=" * 60)
    print("Step 1: Clearing CEDAR folders")
    print("=" * 60)
    client.clear_all()
    print()

    # =========================================================================
    # Step 2: Generate and upload elements
    # =========================================================================
    print("=" * 60)
    print("Step 2: Uploading Elements")
    print("=" * 60)
    schemas = [
        "core.Subject",
        "core.SubjectState",
        "core.TissueSample",
        "core.TissueSampleState",
        "core.Person",
    ]

    for schema in schemas:
        element = element_gen.generate(schema)
        result = client.upload(element, "element")
        if result["success"]:
            print(f"  + {schema}")
        else:
            print(f"  ! {schema}: {result['error'][:80]}")

    print()

    # Fetch elements with real IDs from CEDAR
    uploaded_elements = {}
    for item in client.list_folder(client.folders["elements"]):
        element = client.get_element(item["@id"])
        if element:
            name = element.get("schema:name")
            uploaded_elements[name] = element

    # =========================================================================
    # Step 3: Generate and upload templates
    # =========================================================================
    print("=" * 60)
    print("Step 3: Uploading Templates")
    print("=" * 60)

    # subject-study: Subject + SubjectState (1:N)
    subject = uploaded_elements["subject"]
    subjectstate = uploaded_elements["subjectstate"]
    template1 = template_gen.generate(
        elements=[subject, subjectstate],
        element_ids=[subject["@id"], subjectstate["@id"]],
        name="subject-study",
        description="Subject with multiple states",
        cardinalities=[False, True],
    )
    result = client.upload_template(template1)
    print(f"  + subject-study" if result["success"] else f"  ! subject-study: {result['error'][:80]}")

    # tissue-sample-study: TissueSample + TissueSampleState (1:N)
    tissuesample = uploaded_elements["tissuesample"]
    tissuesamplestate = uploaded_elements["tissuesamplestate"]
    template2 = template_gen.generate(
        elements=[tissuesample, tissuesamplestate],
        element_ids=[tissuesample["@id"], tissuesamplestate["@id"]],
        name="tissue-sample-study",
        description="Tissue sample with multiple states",
        cardinalities=[False, True],
    )
    result = client.upload_template(template2)
    print(f"  + tissue-sample-study" if result["success"] else f"  ! tissue-sample-study: {result['error'][:80]}")

    # person-metadata: Person only
    person = uploaded_elements["person"]
    template3 = template_gen.generate(
        elements=[person],
        element_ids=[person["@id"]],
        name="person-metadata",
        description="Person metadata capture",
        cardinalities=[False],
    )
    result = client.upload_template(template3)
    print(f"  + person-metadata" if result["success"] else f"  ! person-metadata: {result['error'][:80]}")

    print()

    # Fetch templates with real IDs
    templates = {}
    for item in client.list_folder(client.folders["templates"]):
        template = client.get_template(item["@id"])
        if template:
            name = template.get("schema:name")
            templates[name] = template

    # =========================================================================
    # Step 4: Upload test instances (using shared fixtures)
    # =========================================================================
    print("=" * 60)
    print("Step 4: Uploading Test Instances")
    print("=" * 60)

    # Instance using MOCK_SUBJECT_DATA + MOCK_SUBJECTSTATE_DATA from tests/fixtures
    subject_template = templates["subject-study"]
    instance_gen = CEDARInstanceGenerator(subject_template)
    instance1 = instance_gen.create(
        name="Test_Instance",
        description="Test instance using shared fixtures",
        subject_data=MOCK_SUBJECT_DATA.copy(),
        subjectstate_data=MOCK_SUBJECTSTATE_DATA.copy(),
    )
    result = client.upload_instance(instance1)
    instance1_id = result.get("id")
    print(f"  + Test_Instance" if result["success"] else f"  ! Test_Instance: {result['error'][:80]}")

    print()

    # =========================================================================
    # Step 5: Download instances and convert to openMINDS
    # =========================================================================
    print("=" * 60)
    print("Step 5: Converting to openMINDS")
    print("=" * 60)

    # Fetch the uploaded instance
    if instance1_id:
        cedar_instance = client.get_instance(instance1_id)
        if cedar_instance:
            print(f"  Fetched: {cedar_instance.get('schema:name')}")

            # Convert to openMINDS
            collection = converter.convert_instance(cedar_instance)
            print(f"  Converted: {len(list(collection))} objects")

            for obj in collection:
                print(f"    - {type(obj).__name__}")

    print()

    # =========================================================================
    # Step 6: Validate converted objects
    # =========================================================================
    print("=" * 60)
    print("Step 6: Validating openMINDS objects")
    print("=" * 60)

    all_valid = True
    for obj in collection:
        failures = obj.validate()
        if failures:
            print(f"  ! {type(obj).__name__}: {failures}")
            all_valid = False
        else:
            print(f"  + {type(obj).__name__}: valid")

    print()

    # =========================================================================
    # Step 7: Sync to local (tmp folder)
    # =========================================================================
    print("=" * 60)
    print("Step 7: Syncing to scripts/tmp/")
    print("=" * 60)
    client.sync_to_local("scripts/tmp")
    print()

    # =========================================================================
    # Summary
    # =========================================================================
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"Elements:   {len(list(client.list_folder(client.folders['elements'])))}")
    print(f"Templates:  {len(list(client.list_folder(client.folders['templates'])))}")
    print(f"Instances:  {len(list(client.list_folder(client.folders['instances'])))}")
    print(f"Validation: {'PASSED' if all_valid else 'FAILED'}")

    print()
    print("Resource URLs:")
    print("-" * 60)

    print("\nElements:")
    for item in client.list_folder(client.folders["elements"]):
        print(f"  {item.get('schema:name')}: {item['@id']}")

    print("\nTemplates:")
    for item in client.list_folder(client.folders["templates"]):
        print(f"  {item.get('schema:name')}: {item['@id']}")

    print("\nInstances:")
    for item in client.list_folder(client.folders["instances"]):
        print(f"  {item.get('schema:name')}: {item['@id']}")

    return all_valid


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
