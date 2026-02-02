"""CEDAR Template Generator - Combine elements into templates."""

from .cedar_element import BASE_CONTEXT, CEDAR_METADATA


# Context property schema for template validation
def _context_prop(uri: str) -> dict:
    return {"type": "string", "format": "uri", "enum": [uri]}


def _type_prop(type_str: str) -> dict:
    return {"type": "object", "properties": {"@type": {"type": "string", "enum": [type_str]}}}


class CEDARTemplateGenerator:
    """Generate CEDAR Templates from elements."""

    def generate(
        self,
        elements: list[dict],
        element_ids: list[str],
        name: str,
        description: str = "",
        cardinalities: list[bool] | None = None,
    ) -> dict:
        """Create a CEDAR Template embedding elements with their IDs.

        Args:
            cardinalities: List of booleans indicating if element allows multiple (array).
                           Defaults to False for all elements.
        """
        if len(elements) != len(element_ids):
            raise ValueError("elements and element_ids must have same length")

        if cardinalities is None:
            cardinalities = [False] * len(elements)

        properties = self._base_properties(elements)
        for elem, eid, multiple in zip(elements, element_ids, cardinalities):
            elem_copy = elem.copy()
            elem_copy["@id"] = eid
            if multiple:
                # Wrap element in array schema for multiple entries
                properties[elem["schema:name"]] = {
                    "type": "array",
                    "minItems": 0,
                    "items": elem_copy,
                }
            else:
                properties[elem["schema:name"]] = elem_copy

        required = [
            "@context", "@id", "schema:isBasedOn", "schema:name", "schema:description",
            "pav:createdOn", "pav:createdBy", "pav:lastUpdatedOn", "oslc:modifiedBy",
        ] + [elem["schema:name"] for elem in elements]

        return {
            "$schema": "http://json-schema.org/draft-04/schema#",
            "@type": "https://schema.metadatacenter.org/core/Template",
            "@id": f"urn:openminds2cedar:template:{name}",
            "type": "object",
            "title": f"{name} template schema",
            "description": description or f"CEDAR template: {name}",
            "schema:name": name,
            "schema:description": description or f"CEDAR template: {name}",
            **CEDAR_METADATA,
            "@context": {k: v for k, v in BASE_CONTEXT.items() if k not in ("skos", "openminds")},
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
        context_props = {
            "rdfs": _context_prop("http://www.w3.org/2000/01/rdf-schema#"),
            "xsd": _context_prop("http://www.w3.org/2001/XMLSchema#"),
            "pav": _context_prop("http://purl.org/pav/"),
            "schema": _context_prop("http://schema.org/"),
            "oslc": _context_prop("http://open-services.net/ns/core#"),
            "skos": _context_prop("http://www.w3.org/2004/02/skos/core#"),
            "rdfs:label": _type_prop("xsd:string"),
            "schema:isBasedOn": _type_prop("@id"),
            "schema:name": _type_prop("xsd:string"),
            "schema:description": _type_prop("xsd:string"),
            "pav:derivedFrom": _type_prop("@id"),
            "pav:createdOn": _type_prop("xsd:dateTime"),
            "pav:createdBy": _type_prop("@id"),
            "pav:lastUpdatedOn": _type_prop("xsd:dateTime"),
            "oslc:modifiedBy": _type_prop("@id"),
            "skos:notation": _type_prop("xsd:string"),
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
