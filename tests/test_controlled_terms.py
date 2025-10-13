#!/usr/bin/env python3
"""
Test script to demonstrate automatic controlled terms integration
"""

from src.schema_loader import OpenMINDSSchemaLoader
from src.cedar_element_generator import CEDARElementGenerator
import json


def main():
    loader = OpenMINDSSchemaLoader()
    generator = CEDARElementGenerator()

    # Load subject schema
    print("Loading Subject schema from openMINDS...")
    subject_schema = loader.load_schema('core', 'research', 'subject.schema.json')

    # Generate CEDAR element
    print("Generating CEDAR element with controlled terms...")
    element = generator.create_element_from_openminds(subject_schema, 'Subject')

    # Show controlled term fields
    print("\nFields with controlled terms:")
    for field_name, field_spec in element['properties'].items():
        if field_name in ['@context', '@id', '@type']:
            continue

        constraints = field_spec.get('_valueConstraints', {})
        if 'literals' in constraints:
            num_literals = len(constraints['literals'])
            print(f"\n  {field_name}: {num_literals} options")

            # Show first few options
            for lit in constraints['literals'][:5]:
                print(f"    - {lit['label']}")

            if num_literals > 5:
                print(f"    ... and {num_literals - 5} more")

    # Save output
    output_path = 'output/demo/subject_element_with_controlled_terms.json'
    with open(output_path, 'w') as f:
        json.dump(element, f, indent=2)

    print(f"\nSaved element to: {output_path}")
    print("\nControlled terms have been automatically loaded from openMINDS_instances!")


if __name__ == '__main__':
    main()
