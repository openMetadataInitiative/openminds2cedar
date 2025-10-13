#!/usr/bin/env python3
"""
Test Script: Custom Semantic Mappings

This demonstrates how to access and use the custom openminds:termMappings
property that preserves semantic IRIs while maintaining user-friendly interfaces.

This implements Option B from NEXT_STEPS.md: Custom Property approach.
"""

import json
from pathlib import Path

def test_semantic_mappings():
    """Test accessing semantic mappings from CEDAR element"""
    
    element_file = Path("output/cedar_elements/subject_element.json")
    
    if not element_file.exists():
        print("❌ Subject element not found. Run 'python main.py generate' first.")
        return
    
    with open(element_file) as f:
        element = json.load(f)
    
    print("🔍 Testing Custom Semantic Mappings")
    print("=" * 50)
    
    # Test controlled term fields
    controlled_fields = []
    for field_name, field_def in element['properties'].items():
        if field_name not in ['@context', '@id', '@type'] and 'openminds:termMappings' in field_def:
            controlled_fields.append((field_name, field_def))
    
    print(f"Found {len(controlled_fields)} fields with semantic mappings\n")
    
    for field_name, field_def in controlled_fields:
        print(f"📋 Field: {field_name}")
        print("-" * 30)
        
        # UI info
        input_type = field_def['_ui']['inputType']
        literals = field_def['_valueConstraints']['literals']
        print(f"UI Type: {input_type}")
        print(f"Options: {len(literals)} literal choices")
        
        # Semantic mappings
        mappings = field_def['openminds:termMappings']
        print(f"Semantic Mappings: {len(mappings)} entries")
        
        # Show examples
        print("\nExamples:")
        for i, (label, mapping) in enumerate(mappings.items()):
            if i >= 3:  # Show first 3
                break
                
            print(f"  User sees: '{label}'")
            print(f"    openMINDS IRI: {mapping['openminds_id']}")
            if 'ontology_id' in mapping:
                print(f"    Ontology: {mapping['ontology_source']} - {mapping['ontology_id']}")
            print()
        
        if len(mappings) > 3:
            print(f"  ... and {len(mappings) - 3} more mappings")
        
        print()

def demonstrate_lookup_scenarios():
    """Demonstrate practical lookup scenarios"""
    
    print("💡 Practical Usage Scenarios")
    print("=" * 50)
    
    element_file = Path("output/cedar_elements/subject_element.json")
    with open(element_file) as f:
        element = json.load(f)
    
    # Scenario 1: User selects "female" in CEDAR UI
    print("Scenario 1: User selects 'female' in biologicalSex field")
    print("-" * 48)
    
    bio_sex_mappings = element['properties']['biologicalSex']['openminds:termMappings']
    user_selection = "female"
    
    if user_selection in bio_sex_mappings:
        mapping = bio_sex_mappings[user_selection]
        print(f"✅ User selection: {user_selection}")
        print(f"📍 Resolved to openMINDS: {mapping['openminds_id']}")
        print(f"🔗 Ontology reference: {mapping['ontology_id']}")
        print(f"📚 Ontology source: {mapping['ontology_source']}")
    
    print("\n" + "─" * 50 + "\n")
    
    # Scenario 2: Programmatic lookup
    print("Scenario 2: Reverse lookup from IRI")
    print("-" * 35)
    
    target_iri = "https://openminds.om-i.org/instances/species/homoSapiens"
    species_mappings = element['properties']['species']['openminds:termMappings']
    
    # Find by IRI
    found_label = None
    for label, mapping in species_mappings.items():
        if mapping['openminds_id'] == target_iri:
            found_label = label
            break
    
    if found_label:
        print(f"🔍 Looking for IRI: {target_iri}")
        print(f"✅ Found display label: {found_label}")
        print(f"📚 Ontology: {species_mappings[found_label]['ontology_source']}")
    
    print("\n" + "─" * 50 + "\n")
    
    # Scenario 3: Integration possibilities
    print("Scenario 3: Integration Possibilities")
    print("-" * 36)
    
    print("✨ With these mappings, you can:")
    print("  • Convert CEDAR form data back to openMINDS IRIs")
    print("  • Query ontology services using ontology_id")
    print("  • Validate user input against controlled vocabularies")
    print("  • Generate semantic web RDF from form submissions")
    print("  • Create cross-references between systems")

def main():
    """Run all tests"""
    test_semantic_mappings()
    print()
    demonstrate_lookup_scenarios()
    
    print("\n🎉 Custom Semantic Mappings Test Complete!")
    print("\nNext steps:")
    print("  • See NEXT_STEPS.md for Phase 2 (InterLex integration)")
    print("  • Try uploading to CEDAR with: python main.py upload")
    print("  • Explore hybrid approaches for advanced use cases")

if __name__ == "__main__":
    main()