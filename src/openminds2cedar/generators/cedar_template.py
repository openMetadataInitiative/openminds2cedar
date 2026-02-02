"""
CEDAR Template Generator - Combine uploaded elements into templates.

Usage example (after elements are uploaded and synced locally):

    import json
    from pathlib import Path
    from openminds2cedar.generators import CEDARTemplateGenerator
    from openminds2cedar.api import CEDARClient

    client = CEDARClient()
    gen = CEDARTemplateGenerator()

    # Load synced elements from local data/cedar/elements/
    elements_dir = Path('data/cedar/elements')
    elements = []
    element_ids = []

    for name in ['subject', 'subjectstate']:
        with open(elements_dir / f'{name}.json') as f:
            elem = json.load(f)
        elements.append(elem)
        element_ids.append(elem['@id'])

    # Generate and upload template
    template = gen.generate(elements, element_ids, 'my-template', 'Description')
    result = client.validate_template(template)
    if result['valid']:
        result = client.upload_template(template)
        print(f'Template ID: {result[\"id\"]}')
"""


class CEDARTemplateGenerator:
    """Generate CEDAR Templates from uploaded elements."""

    def generate(
        self,
        elements: list[dict],
        element_ids: list[str],
        name: str,
        description: str = "",
    ) -> dict:
        """
        Create a CEDAR Template embedding elements with their uploaded IDs.

        Args:
            elements: Element dicts (loaded from synced JSON files)
            element_ids: IDs from the uploaded elements (elem['@id'])
            name: Template name
            description: Template description

        Returns:
            CEDAR Template dict ready for validation and upload
        """
        if len(elements) != len(element_ids):
            raise ValueError("elements and element_ids must have same length")

        # Build properties with embedded elements
        properties = self._base_properties(elements)
        for elem, eid in zip(elements, element_ids):
            elem_copy = elem.copy()
            elem_copy["@id"] = eid
            properties[elem["schema:name"]] = elem_copy

        # Required array must include base fields + all element names
        required = [
            "@context", "@id", "schema:isBasedOn", "schema:name", "schema:description",
            "pav:createdOn", "pav:createdBy", "pav:lastUpdatedOn", "oslc:modifiedBy",
        ]
        required.extend(elem["schema:name"] for elem in elements)

        return {
            "$schema": "http://json-schema.org/draft-04/schema#",
            "@type": "https://schema.metadatacenter.org/core/Template",
            "@id": None,
            "type": "object",
            "title": f"{name} template schema",
            "description": description or f"CEDAR template: {name}",
            "schema:name": name,
            "schema:description": description or f"CEDAR template: {name}",
            "schema:schemaVersion": "1.6.0",
            "pav:version": "0.0.1",
            "pav:createdOn": None,
            "pav:createdBy": None,
            "pav:lastUpdatedOn": None,
            "oslc:modifiedBy": None,
            "bibo:status": "bibo:draft",
            "@context": {
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
                "oslc:modifiedBy": {"@type": "@id"},
            },
            "properties": properties,
            "_ui": {
                "order": [elem["schema:name"] for elem in elements],
                "propertyLabels": {elem["schema:name"]: elem["title"] for elem in elements},
                "propertyDescriptions": {elem["schema:name"]: elem.get("schema:description", "") for elem in elements},
            },
            "required": required,
            "additionalProperties": False,
        }

    def _base_properties(self, elements: list[dict]) -> dict:
        """Template-level properties including @context structure."""
        # Build @context properties with all required fields
        context_props = {
            "rdfs": {"type": "string", "format": "uri", "enum": ["http://www.w3.org/2000/01/rdf-schema#"]},
            "xsd": {"type": "string", "format": "uri", "enum": ["http://www.w3.org/2001/XMLSchema#"]},
            "pav": {"type": "string", "format": "uri", "enum": ["http://purl.org/pav/"]},
            "schema": {"type": "string", "format": "uri", "enum": ["http://schema.org/"]},
            "oslc": {"type": "string", "format": "uri", "enum": ["http://open-services.net/ns/core#"]},
            "skos": {"type": "string", "format": "uri", "enum": ["http://www.w3.org/2004/02/skos/core#"]},
            "rdfs:label": {"type": "object", "properties": {"@type": {"type": "string", "enum": ["xsd:string"]}}},
            "schema:isBasedOn": {"type": "object", "properties": {"@type": {"type": "string", "enum": ["@id"]}}},
            "schema:name": {"type": "object", "properties": {"@type": {"type": "string", "enum": ["xsd:string"]}}},
            "schema:description": {"type": "object", "properties": {"@type": {"type": "string", "enum": ["xsd:string"]}}},
            "pav:derivedFrom": {"type": "object", "properties": {"@type": {"type": "string", "enum": ["@id"]}}},
            "pav:createdOn": {"type": "object", "properties": {"@type": {"type": "string", "enum": ["xsd:dateTime"]}}},
            "pav:createdBy": {"type": "object", "properties": {"@type": {"type": "string", "enum": ["@id"]}}},
            "pav:lastUpdatedOn": {"type": "object", "properties": {"@type": {"type": "string", "enum": ["xsd:dateTime"]}}},
            "oslc:modifiedBy": {"type": "object", "properties": {"@type": {"type": "string", "enum": ["@id"]}}},
            "skos:notation": {"type": "object", "properties": {"@type": {"type": "string", "enum": ["xsd:string"]}}},
        }

        # Add element type URIs to context
        for elem in elements:
            elem_name = elem.get("schema:name", "element")
            source_type = elem.get("openminds:sourceType", f"https://openminds.om-i.org/types/{elem_name}")
            context_props[elem_name] = {"enum": [source_type]}

        return {
            "@context": {
                "type": "object",
                "properties": context_props,
                "required": [
                    "xsd", "pav", "schema", "oslc", "schema:isBasedOn", "schema:name",
                    "schema:description", "pav:createdOn", "pav:createdBy",
                    "pav:lastUpdatedOn", "oslc:modifiedBy",
                ],
                "additionalProperties": False,
            },
            "@id": {"type": ["string", "null"], "format": "uri"},
            "@type": {
                "oneOf": [
                    {"type": "string", "format": "uri"},
                    {"type": "array", "minItems": 1, "items": {"type": "string", "format": "uri"}, "uniqueItems": True},
                ]
            },
            "schema:isBasedOn": {"type": "string", "format": "uri"},
            "schema:name": {"type": "string", "minLength": 1},
            "schema:description": {"type": "string"},
            "pav:derivedFrom": {"type": "string", "format": "uri"},
            "pav:createdOn": {"type": ["string", "null"], "format": "date-time"},
            "pav:createdBy": {"type": ["string", "null"], "format": "uri"},
            "pav:lastUpdatedOn": {"type": ["string", "null"], "format": "date-time"},
            "oslc:modifiedBy": {"type": ["string", "null"], "format": "uri"},
        }
