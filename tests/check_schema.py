#!/usr/bin/env python3
"""Check what's in the species field spec"""

import sys
sys.path.insert(0, 'src')
import json

from schema_loader import OpenMINDSSchemaLoader

# Load schema
loader = OpenMINDSSchemaLoader()
subject_schema = loader.load_schema('core', 'research', 'subject.schema.json')

# Check species field
species_key = "https://openminds.om-i.org/props/species"
if species_key in subject_schema.get("properties", {}):
    species_spec = subject_schema["properties"][species_key]
    print("Species field specification:")
    print(json.dumps(species_spec, indent=2))

# Check biologicalSex field
biosex_key = "https://openminds.om-i.org/props/biologicalSex"
if biosex_key in subject_schema.get("properties", {}):
    biosex_spec = subject_schema["properties"][biosex_key]
    print("\n\nBiologicalSex field specification:")
    print(json.dumps(biosex_spec, indent=2))
