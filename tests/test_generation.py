#!/usr/bin/env python3
"""
Test complete element generation workflow with controlled terms

This test verifies that:
1. Schema loads correctly from openMINDS submodule
2. Element generation includes controlled term fields
3. Controlled term fields have correct structure and values
4. Output can be saved successfully
"""

import sys
import os
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from schema_loader import OpenMINDSSchemaLoader
from cedar_element_generator import CEDARElementGenerator


def test_subject_element_generation():
    """Test generating Subject element with controlled terms"""
    print("\nTest: Subject Element Generation with Controlled Terms")
    print("=" * 60)

    # Load schema
    print("\n1. Loading schema...")
    loader = OpenMINDSSchemaLoader()
    subject_schema = loader.load_schema('core', 'research', 'subject.schema.json')
    assert subject_schema is not None, "Schema should load successfully"
    print("   ✓ Schema loaded")

    # Generate element
    print("\n2. Generating CEDAR element...")
    generator = CEDARElementGenerator()
    element = generator.create_element_from_openminds(subject_schema, "Subject")
    assert element is not None, "Element should be generated"
    assert "properties" in element, "Element should have properties"
    print("   ✓ Element generated")

    # Save to output
    print("\n3. Saving element...")
    os.makedirs("output/demo", exist_ok=True)
    output_file = "output/demo/subject_element_with_controlled_terms.json"

    with open(output_file, 'w') as f:
        json.dump(element, f, indent=2)

    assert os.path.exists(output_file), "Output file should exist"
    print(f"   ✓ Saved to: {output_file}")

    # Verify controlled fields
    print("\n4. Verifying controlled term fields...")

    # Check species field
    if "species" in element["properties"]:
        species_constraints = element["properties"]["species"]["_valueConstraints"]
        species_literals = species_constraints.get("literals", [])
        assert len(species_literals) > 0, "Species should have controlled options"
        print(f"   ✓ Species has {len(species_literals)} controlled options")

    # Check biologicalSex field
    if "biologicalSex" in element["properties"]:
        biosex_constraints = element["properties"]["biologicalSex"]["_valueConstraints"]
        biosex_literals = biosex_constraints.get("literals", [])
        assert len(biosex_literals) > 0, "BiologicalSex should have controlled options"
        print(f"   ✓ BiologicalSex has {len(biosex_literals)} controlled options")

    # Count total controlled fields
    controlled_fields = 0
    for field_name in element["properties"]:
        if field_name not in ["@context", "@id", "@type"]:
            field = element["properties"][field_name]
            constraints = field.get("_valueConstraints", {})
            if constraints.get("literals"):
                controlled_fields += 1

    assert controlled_fields > 0, "Element should have at least one controlled field"
    print(f"   ✓ Total controlled fields: {controlled_fields}")

    # Verify inputType selection
    print("\n5. Verifying inputType selection...")

    if "biologicalSex" in element["properties"]:
        biosex_inputType = element["properties"]["biologicalSex"]["_ui"]["inputType"]
        biosex_count = len(element["properties"]["biologicalSex"]["_valueConstraints"]["literals"])
        if biosex_count <= 5:
            assert biosex_inputType == "radio", "Small lists should use radio buttons"
            print(f"   ✓ BiologicalSex ({biosex_count} options) uses radio buttons")

    if "species" in element["properties"]:
        species_inputType = element["properties"]["species"]["_ui"]["inputType"]
        species_count = len(element["properties"]["species"]["_valueConstraints"]["literals"])
        if species_count > 5:
            assert species_inputType == "list", "Large lists should use dropdown"
            print(f"   ✓ Species ({species_count} options) uses dropdown list")

    print("\n" + "=" * 60)
    print("✓ All tests passed")

    return element


if __name__ == "__main__":
    try:
        element = test_subject_element_generation()
        print("\n✓ Test completed successfully")
        sys.exit(0)
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
