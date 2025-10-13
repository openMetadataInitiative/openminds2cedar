#!/usr/bin/env python3
"""
OpenMINDS to CEDAR Element Converter

This module converts openMINDS JSON Schema metadata to CEDAR TemplateElement format,
with automatic controlled vocabulary integration and smart UI selection.

Key Assumptions:
- openMINDS uses full URLs as property keys (e.g., https://openminds.om-i.org/props/biologicalSex)
- CEDAR requires simple field names (e.g., biologicalSex)
- CEDAR @context preserves semantic URLs for JSON-LD compatibility
- All description fields must be strings, never null

Major Differences Handled:
1. Property naming: URL extraction for CEDAR compliance
2. Field structure: Flat properties -> nested TemplateField objects
3. Type mapping: openMINDS types -> CEDAR inputType + _valueConstraints
4. Controlled terms: Automatic detection and literal generation
5. Required fields: Multiple levels (element, field, field.properties)

Controlled Terms Integration:
- Detects fields with @type enum in if/then/else structure
- Loads instances from openMINDS_instances
- Creates appropriate inputType (radio, list, checkbox)
- Generates literals with labels for CEDAR UI

Critical CEDAR Quirks:
1. Literal fields (list/radio/checkbox) use @value, not @id
2. Link fields (controlled-term/link) use @id, not @value
3. Descriptions cannot be null (use empty string)
4. Required fields must not contain duplicates
5. Context preservation: Clean names in properties, URLs in @context

Valid CEDAR inputType Values (from validation):
- textfield, textarea, radio, checkbox, boolean, temporal,
  email, list, numeric, phone-number, attribute-value

Design Decision: List/Radio vs Ontology
- Current: Use literals from openMINDS for exact control and simple UI
- Future: Could integrate with BioPortal/InterLex (see NEXT_STEPS.md)
- Trade-off: User-friendly but loses direct semantic IRI references
"""

import json
import uuid
import re
from typing import Dict, Optional
from controlled_terms_loader import ControlledTermsLoader


class CEDARElementGenerator:
    """
    Generate CEDAR Elements from openMINDS schemas

    CEDAR TemplateElement Structure:
    - @type: Must be 'https://schema.metadatacenter.org/core/TemplateElement'
    - @context: JSON-LD context with namespace prefixes
    - properties: Dictionary of field definitions (each is a TemplateField)
    - _ui: UI metadata (field order, labels, descriptions)
    - required: Array of required field names (includes @context, @id)
    - schema:schemaVersion: CEDAR version (default: 1.6.0)
    """

    def __init__(self, cedar_version: str = "1.6.0"):
        """
        Initialize the converter

        Args:
            cedar_version: CEDAR schema version to use (default: 1.6.0)
        """
        self.cedar_version = cedar_version
        self.controlled_terms_loader = ControlledTermsLoader()

    def _extract_field_name(self, property_name: str) -> Optional[str]:
        """
        Extract clean field name from openMINDS property URL

        openMINDS Quirk: Properties use full URLs as keys
        Example: https://openminds.om-i.org/props/biologicalSex

        CEDAR Requirement: Simple field names only
        Example: biologicalSex

        Handling:
        - Skip reserved JSON-LD fields (@id, @type, @context)
        - Extract last segment from URLs (split by '/')
        - Preserve non-URL names as-is

        Args:
            property_name: Original property key from openMINDS

        Returns:
            Clean field name or None if field should be skipped
        """
        # Reserved fields: CEDAR adds these automatically, skip from openMINDS
        if property_name in ("@id", "@type", "@context"):
            return None

        # URL-based property: Extract last segment
        # https://openminds.om-i.org/props/biologicalSex -> biologicalSex
        if property_name.startswith("http"):
            return property_name.split("/")[-1]

        # Already a simple name
        return property_name

    def create_element_from_openminds(self, openminds_schema: Dict,
                                      element_name: Optional[str] = None) -> Dict:
        """
        Create a CEDAR Element from an openMINDS schema

        Main conversion logic that:
        1. Extracts metadata (title, description)
        2. Initializes CEDAR element structure
        3. Converts each openMINDS property to CEDAR field
        4. Handles required fields at multiple levels
        5. Preserves semantic URLs in @context

        Args:
            openminds_schema: openMINDS JSON Schema dictionary
            element_name: Optional custom name (overrides schema title)

        Returns:
            CEDAR TemplateElement dictionary (JSON-LD compliant)
        """
        title = element_name or openminds_schema.get("title", "Unnamed Element")
        description = openminds_schema.get("description", f"{title} generated from openMINDS schema")

        # CEDAR Element skeleton with required top-level properties
        # Note: @id is null (CEDAR assigns UUID on upload)
        element = {
            "@type": "https://schema.metadatacenter.org/core/TemplateElement",
            "@context": self._create_element_context(),
            "type": "object",
            "title": f"{title} element schema",
            "description": f"{title} element schema generated from openMINDS",
            "_ui": {
                "order": [],
                "propertyLabels": {},
                "propertyDescriptions": {}
            },
            "properties": {
                "@context": {
                    "type": "object",
                    "properties": {},
                    "additionalProperties": False,
                    "required": []
                },
                "@id": {
                    "type": "string",
                    "format": "uri"
                },
                "@type": {
                    "oneOf": [
                        {"type": "string", "format": "uri"},
                        {
                            "type": "array",
                            "minItems": 1,
                            "items": {"type": "string", "format": "uri"},
                            "uniqueItems": True
                        }
                    ]
                }
            },
            "schema:name": title.lower().replace(" ", "-"),
            "schema:description": description,
            "required": ["@context", "@id"],
            "pav:createdOn": None,
            "pav:createdBy": None,
            "pav:lastUpdatedOn": None,
            "oslc:modifiedBy": None,
            "schema:schemaVersion": self.cedar_version,
            "additionalProperties": False,
            "pav:version": "0.0.1",
            "bibo:status": "bibo:draft",
            "@id": None,
            "$schema": "http://json-schema.org/draft-04/schema#"
        }

        # Process openMINDS properties and convert to CEDAR fields
        # Each openMINDS property becomes a nested TemplateField in CEDAR
        if "properties" in openminds_schema:
            for orig_field_name, field_spec in openminds_schema["properties"].items():
                # Step 1: Extract clean field name from URL
                # Example: https://openminds.om-i.org/props/biologicalSex -> biologicalSex
                field_name = self._extract_field_name(orig_field_name)
                if not field_name:
                    continue  # Skip reserved fields (@id, @type, @context)

                # Step 2: Check if field is required in openMINDS
                # Note: Use original URL name for lookup
                is_required = orig_field_name in openminds_schema.get("required", [])

                # Step 3: Create CEDAR TemplateField based on openMINDS type
                cedar_field = self._create_cedar_field(field_name, field_spec, is_required)

                # Step 4: Add field to element properties
                element["properties"][field_name] = cedar_field

                # Step 5: Add UI metadata
                element["_ui"]["order"].append(field_name)
                element["_ui"]["propertyLabels"][field_name] = field_name

                # CEDAR Quirk: propertyDescriptions must be string, not null
                # Use empty string if description is missing
                element["_ui"]["propertyDescriptions"][field_name] = field_spec.get("description") or ""

                # Step 6: Add to element-level required array
                # CEDAR requires @context and @id (pre-added), plus user fields
                # Duplicate check prevents validation errors
                if is_required and field_name not in element["required"]:
                    element["required"].append(field_name)

                # Step 7: Preserve semantic URL in @context for JSON-LD
                # This maintains openMINDS semantics while using simple names
                property_iri = orig_field_name if orig_field_name.startswith("http") else self._generate_property_iri(field_name)
                element["properties"]["@context"]["properties"][field_name] = {
                    "enum": [property_iri]
                }
                element["properties"]["@context"]["required"].append(field_name)

        return element

    def _create_element_context(self) -> Dict:
        """Create the @context for a CEDAR Element"""
        return {
            "xsd": "http://www.w3.org/2001/XMLSchema#",
            "pav": "http://purl.org/pav/",
            "bibo": "http://purl.org/ontology/bibo/",
            "oslc": "http://open-services.net/ns/core#",
            "schema": "http://schema.org/",
            "schema:name": {"@type": "xsd:string"},
            "schema:description": {"@type": "xsd:string"},
            "pav:createdOn": {"@type": "xsd:dateTime"},
            "pav:createdBy": {"@type": "@id"},
            "pav:lastUpdatedOn": {"@type": "xsd:dateTime"},
            "oslc:modifiedBy": {"@type": "@id"}
        }

    def _create_cedar_field(self, field_name: str, field_spec: Dict, is_required: bool) -> Dict:
        """
        Create a CEDAR TemplateField from openMINDS field specification

        Type Detection Order (priority-based):
        1. Numeric: type is 'number' or 'integer'
        2. Controlled term: has openMINDS @type enum indicating controlled vocabulary
        3. Controlled term with ontology: has '_linkedTypes' property
        4. Controlled term (IRI): format is 'iri'
        5. Multi-value controlled term: type 'array' with IRI items
        6. Default: text field

        Mapping Logic:
        - openMINDS 'type' -> CEDAR 'inputType' + '_valueConstraints'
        - openMINDS @type enum -> Check for controlled term instances
        - openMINDS '_linkedTypes' -> CEDAR ontology branches (PATO, NCBITAXON)
        - openMINDS 'description' -> CEDAR 'schema:description' (never null)

        Args:
            field_name: Clean field name (already extracted from URL)
            field_spec: openMINDS field specification
            is_required: Whether field is required

        Returns:
            CEDAR TemplateField dictionary
        """
        field_type = field_spec.get("type")

        # CEDAR Quirk: Descriptions must be strings, never None
        # Try description first, fallback to _instruction, then empty string
        description = field_spec.get("description") or field_spec.get("_instruction") or ""

        # Type mapping: Check in priority order
        # 1. Numeric fields: Direct mapping to CEDAR numeric input
        if field_type in ("number", "integer"):
            return self._create_numeric_field(field_name, description, is_required)

        # 2. Check if this is a controlled term field (has @type enum in then/else structure)
        # openMINDS uses if/then/else with @type enums to indicate controlled vocabularies
        if self._is_controlled_term_field(field_spec):
            return self._create_controlled_term_field(field_name, field_spec, description, is_required)

        # 3. Controlled terms with ontology: Check for semantic links
        # openMINDS uses _linkedTypes to reference ontology concepts
        if "_linkedTypes" in field_spec or field_spec.get("format") == "iri":
            return self._create_controlled_term_field(field_name, field_spec, description, is_required)

        # 4. Array of IRIs: Multi-select controlled term
        if field_type == "array" and field_spec.get("items", {}).get("format") == "iri":
            return self._create_controlled_term_field(field_name, field_spec, description, is_required, multiple=True)

        # 5. Default: Simple text field for strings and untyped fields
        return self._create_text_field(field_name, description, is_required)

    def _is_controlled_term_field(self, field_spec: Dict) -> bool:
        """
        Check if field is a controlled term by looking for @type enum

        openMINDS uses if/then/else structure with @type enum to indicate controlled terms
        Example: @type: enum: ["https://openminds.om-i.org/types/Species"]
        """
        # Check in 'then' branch for @type enum
        then_props = field_spec.get("then", {}).get("properties", {})
        if "@type" in then_props:
            type_enum = then_props["@type"].get("enum", [])
            # Look for openMINDS type URLs
            return any("openminds.om-i.org/types/" in url for url in type_enum)

        return False

    def _create_text_field(self, field_name: str, description: str, is_required: bool) -> Dict:
        """Create a CEDAR text field"""
        return {
            "@type": "https://schema.metadatacenter.org/core/TemplateField",
            "@context": self._create_field_context(),
            "type": "object",
            "title": f"{field_name} field schema",
            "description": f"{field_name} field schema generated from openMINDS",
            "_ui": {
                "inputType": "textfield"
            },
            "_valueConstraints": {
                "requiredValue": is_required
            },
            "properties": {
                "@type": {
                    "oneOf": [
                        {"type": "string", "format": "uri"},
                        {
                            "type": "array",
                            "minItems": 1,
                            "items": {"type": "string", "format": "uri"},
                            "uniqueItems": True
                        }
                    ]
                },
                "@value": {
                    "type": ["string", "null"]
                },
                "rdfs:label": {
                    "type": ["string", "null"]
                }
            },
            "required": ["@value"] if is_required else [],
            "schema:name": field_name,
            "schema:description": description,
            "pav:createdOn": None,
            "pav:createdBy": None,
            "pav:lastUpdatedOn": None,
            "oslc:modifiedBy": None,
            "schema:schemaVersion": self.cedar_version,
            "additionalProperties": False,
            "skos:prefLabel": re.sub(r'([A-Z])', r' \1', field_name).strip().title(),
            "@id": f"https://repo.metadatacenter.org/template-fields/{uuid.uuid4()}",
            "$schema": "http://json-schema.org/draft-04/schema#"
        }

    def _create_numeric_field(self, field_name: str, description: str, is_required: bool) -> Dict:
        """Create a CEDAR numeric field"""
        return {
            "@type": "https://schema.metadatacenter.org/core/TemplateField",
            "@context": self._create_field_context(),
            "type": "object",
            "title": f"{field_name} field schema",
            "description": f"{field_name} field schema generated from openMINDS",
            "_ui": {
                "inputType": "numeric"
            },
            "_valueConstraints": {
                "requiredValue": is_required,
                "numberType": "xsd:decimal"
            },
            "properties": {
                "@value": {
                    "type": ["string", "null"]
                },
                "rdfs:label": {
                    "type": ["string", "null"]
                },
                "@type": {
                    "type": "string",
                    "format": "uri"
                }
            },
            "required": ["@value", "@type"] if is_required else [],
            "schema:name": field_name,
            "schema:description": description,
            "pav:createdOn": None,
            "pav:createdBy": None,
            "pav:lastUpdatedOn": None,
            "oslc:modifiedBy": None,
            "schema:schemaVersion": self.cedar_version,
            "additionalProperties": False,
            "skos:prefLabel": field_name.replace("_", " ").title(),
            "@id": f"https://repo.metadatacenter.org/template-fields/{uuid.uuid4()}",
            "$schema": "http://json-schema.org/draft-04/schema#"
        }

    def _create_controlled_term_field(self, field_name: str, field_spec: Dict,
                                     description: str, is_required: bool, multiple: bool = False) -> Dict:
        """
        Create a CEDAR controlled term field with value constraints

        If openMINDS has controlled term instances for this field, they are automatically
        loaded and added as literals in the CEDAR field.

        Args:
            field_name: Clean field name
            field_spec: openMINDS field specification
            description: Field description
            is_required: Whether field is required
            multiple: Allow multiple values (for arrays)

        Returns:
            CEDAR TemplateField with value constraints (literals if available)
        """
        # Check if controlled terms exist in openMINDS_instances
        ct_config = self.controlled_terms_loader.get_cedar_value_constraints(
            field_name, is_required, multiple
        )

        # Use controlled terms config or create default link field
        if ct_config:
            input_type = ct_config["inputType"]
            value_constraints = ct_config["valueConstraints"]
        else:
            input_type = "link"
            value_constraints = {
                "requiredValue": is_required,
                "multipleChoice": multiple
            }

        # CRITICAL CEDAR QUIRK: @value vs @id property structure
        #
        # This was discovered through CEDAR validation errors. CEDAR schema defines
        # different required properties based on inputType:
        #
        # Literal fields (list, radio, checkbox, textfield, etc.):
        # - Store value in @value property
        # - Used when value is a literal string or number
        # - Example: User selects "female" -> stored as @value: "female"
        #
        # Link fields (controlled-term, link):
        # - Store value in @id property
        # - Used when value is an IRI/URI reference
        # - Example: User enters IRI -> stored as @id: "http://..."
        #
        # Why this matters:
        # - Controls what user sees in CEDAR UI (text vs IRI input)
        # - Affects validation (different schemas for @value vs @id)
        # - Impacts data model (literals vs references)
        #
        # Decision: Use @value for controlled terms to get user-friendly labels
        # Trade-off: Lose direct IRI references (see NEXT_STEPS.md for solutions)
        if input_type in ["list", "radio", "checkbox"]:
            properties = {
                "@type": {
                    "oneOf": [
                        {"type": "string", "format": "uri"},
                        {
                            "type": "array",
                            "minItems": 1,
                            "items": {"type": "string", "format": "uri"},
                            "uniqueItems": True
                        }
                    ]
                },
                "@value": {
                    "type": ["string", "null"]
                },
                "rdfs:label": {
                    "type": ["string", "null"]
                }
            }
            required_props = ["@value"] if is_required else []
        else:
            # Link fields use @id
            properties = {
                "@type": {
                    "oneOf": [
                        {"type": "string", "format": "uri"},
                        {
                            "type": "array",
                            "minItems": 1,
                            "items": {"type": "string", "format": "uri"},
                            "uniqueItems": True
                        }
                    ]
                },
                "rdfs:label": {
                    "type": ["string", "null"]
                },
                "@id": {
                    "type": "string",
                    "format": "uri"
                }
            }
            required_props = ["@id"] if is_required else []

        field = {
            "@type": "https://schema.metadatacenter.org/core/TemplateField",
            "@context": self._create_field_context(),
            "type": "object",
            "title": f"{field_name} field schema",
            "description": f"{field_name} field schema generated from openMINDS",
            "_ui": {
                "inputType": input_type
            },
            "_valueConstraints": value_constraints,
            "properties": properties,
            "required": required_props,
            "schema:name": field_name,
            "schema:description": description,
            "pav:createdOn": None,
            "pav:createdBy": None,
            "pav:lastUpdatedOn": None,
            "oslc:modifiedBy": None,
            "schema:schemaVersion": self.cedar_version,
            "additionalProperties": False,
            "skos:prefLabel": field_name.replace("_", " ").title(),
            "@id": f"https://repo.metadatacenter.org/template-fields/{uuid.uuid4()}",
            "$schema": "http://json-schema.org/draft-04/schema#"
        }

        return field

    def _create_field_context(self) -> Dict:
        """Create @context for a CEDAR field"""
        return {
            "xsd": "http://www.w3.org/2001/XMLSchema#",
            "pav": "http://purl.org/pav/",
            "bibo": "http://purl.org/ontology/bibo/",
            "oslc": "http://open-services.net/ns/core#",
            "schema": "http://schema.org/",
            "skos": "http://www.w3.org/2004/02/skos/core#",
            "schema:name": {"@type": "xsd:string"},
            "schema:description": {"@type": "xsd:string"},
            "skos:prefLabel": {"@type": "xsd:string"},
            "skos:altLabel": {"@type": "xsd:string"},
            "pav:createdOn": {"@type": "xsd:dateTime"},
            "pav:createdBy": {"@type": "@id"},
            "pav:lastUpdatedOn": {"@type": "xsd:dateTime"},
            "oslc:modifiedBy": {"@type": "@id"}
        }

    def _generate_property_iri(self, field_name: str) -> str:
        """Generate a property IRI for a field in the @context"""
        return f"https://schema.metadatacenter.org/properties/{uuid.uuid4()}"

    def save_element(self, element: Dict, output_path: str):
        """Save CEDAR element to JSON file"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(element, f, indent=2, ensure_ascii=False)
        print(f"Saved: {output_path}")
