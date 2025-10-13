#!/usr/bin/env python3
"""Test CEDAR validation with the updated element"""

import sys
sys.path.insert(0, 'src')
import json
from dotenv import load_dotenv

from cedar_api import CEDARAPIClient

# Load environment
load_dotenv()

# Regenerate element with latest code
from schema_loader import OpenMINDSSchemaLoader
from cedar_element_generator import CEDARElementGenerator

loader = OpenMINDSSchemaLoader()
subject_schema = loader.load_schema('core', 'research', 'subject.schema.json')
generator = CEDARElementGenerator()
element = generator.create_element_from_openminds(subject_schema, 'Subject')

# Test validation
client = CEDARAPIClient()
if client.api_key:
    print("Validating element with CEDAR...")
    try:
        result = client.validate_element(element)
        print(f"  Raw result: {result}")
        
        validates = result.get('validates') == 'true' or result.get('validates') == True
        print(f"  Result: {validates}")
        
        if not validates:
            errors = result.get('errors', [])
            warnings = result.get('warnings', [])
            print(f"  Errors: {len(errors)}")
            for i, error in enumerate(errors[:10]):  # Show first 10 errors
                print(f"    {i+1}. {error}")
            if warnings:
                print(f"  Warnings: {len(warnings)}")
                for i, warning in enumerate(warnings[:5]):
                    print(f"    W{i+1}. {warning}")
        else:
            print("  ✓ Element validates successfully!")
            
    except Exception as e:
        print(f"  Validation error: {e}")
else:
    print("No CEDAR API key found - skipping validation")