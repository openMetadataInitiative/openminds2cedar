#!/usr/bin/env python3
"""Debug cedar_element_generator controlled terms integration"""

import sys
sys.path.insert(0, 'src')
import json

from schema_loader import OpenMINDSSchemaLoader
from cedar_element_generator import CEDARElementGenerator

# Load schema
loader = OpenMINDSSchemaLoader()
subject_schema = loader.load_schema('core', 'research', 'subject.schema.json')

# Check what fields are in the schema
print("Fields in subject schema:")
for prop_name in subject_schema.get("properties", {}).keys():
    if not prop_name.startswith("@"):
        print(f"  - {prop_name}")

# Create generator and check loader
generator = CEDARElementGenerator()
print(f"\nGenerator has loader: {generator.controlled_terms_loader is not None}")
print(f"Loader USE_ONTOLOGY: {generator.controlled_terms_loader.USE_ONTOLOGY}")
print(f"Loader USE_LITERALS: {generator.controlled_terms_loader.USE_LITERALS}")

# Test getting constraints directly
print("\n--- Testing direct constraint retrieval ---")
species_result = generator.controlled_terms_loader.get_cedar_value_constraints("species", True)
print(f"species constraints: {species_result is not None}")
if species_result:
    print(f"  Has ontologies: {len(species_result.get('ontologies', [])) > 0}")

biosex_result = generator.controlled_terms_loader.get_cedar_value_constraints("biologicalSex", False)
print(f"biologicalSex constraints: {biosex_result is not None}")
if biosex_result:
    print(f"  Has literals: {len(biosex_result.get('literals', [])) > 0}")

# Now generate the element
print("\n--- Generating element ---")
element = generator.create_element_from_openminds(subject_schema, "Subject")

# Check what ended up in the element
print("\nChecking generated element...")
if "species" in element["properties"]:
    species_field = element["properties"]["species"]
    constraints = species_field.get("_valueConstraints", {})
    print(f"species _valueConstraints keys: {list(constraints.keys())}")
    print(f"  ontologies: {constraints.get('ontologies', [])}")
