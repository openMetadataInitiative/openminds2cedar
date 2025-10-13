#!/usr/bin/env python3
"""Debug controlled terms loader"""

import sys
sys.path.insert(0, 'src')

from controlled_terms_loader import ControlledTermsLoader

# Test loader directly
loader = ControlledTermsLoader()

print("Testing ControlledTermsLoader...")
print(f"USE_ONTOLOGY: {loader.USE_ONTOLOGY}")
print(f"USE_LITERALS: {loader.USE_LITERALS}")

# Test species
print("\n--- Testing species ---")
species_constraints = loader.get_cedar_value_constraints("species", is_required=True)
print(f"Result: {species_constraints}")

# Test biologicalSex
print("\n--- Testing biologicalSex ---")
bio_sex_constraints = loader.get_cedar_value_constraints("biologicalSex", is_required=False)
print(f"Result: {bio_sex_constraints}")

# Test unknown field
print("\n--- Testing internalIdentifier (not a controlled term) ---")
other_constraints = loader.get_cedar_value_constraints("internalIdentifier", is_required=False)
print(f"Result: {other_constraints}")
