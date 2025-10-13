#!/usr/bin/env python3
"""Quick test to verify controlled terms integration"""

import sys
sys.path.insert(0, 'src')
import json

from schema_loader import OpenMINDSSchemaLoader
from cedar_element_generator import CEDARElementGenerator

# Load schema
loader = OpenMINDSSchemaLoader()
subject_schema = loader.load_schema('core', 'research', 'subject.schema.json')

# Generate element
generator = CEDARElementGenerator()
element = generator.create_element_from_openminds(subject_schema, "Subject")

# Check species field
species_constraints = element["properties"]["species"]["_valueConstraints"]
print("Species field _valueConstraints:")
print(json.dumps(species_constraints, indent=2))

has_ontology = len(species_constraints.get("ontologies", [])) > 0
print(f"\nSpecies has ontology constraints: {has_ontology}")

# Check biologicalSex field
bio_sex_constraints = element["properties"]["biologicalSex"]["_valueConstraints"]
print("\nBiologicalSex field _valueConstraints:")
print(json.dumps(bio_sex_constraints, indent=2))

has_literals = len(bio_sex_constraints.get("literals", [])) > 0
print(f"\nBiologicalSex has literal constraints: {has_literals}")

species_has_literals = len(element["properties"]["species"]["_valueConstraints"].get("literals", [])) > 0

if has_literals and species_has_literals:
    print("\n✓ openMINDS controlled terms integration successful!")
    print(f"✓ Species has {len(element['properties']['species']['_valueConstraints']['literals'])} species options")
    print(f"✓ BiologicalSex has {len(element['properties']['biologicalSex']['_valueConstraints']['literals'])} sex options")
else:
    print("\n✗ Integration not as expected")
    print(f"  Expected: both fields with openMINDS literals")
    print(f"  Actual: species_literals={species_has_literals}, biologicalSex_literals={has_literals}")
