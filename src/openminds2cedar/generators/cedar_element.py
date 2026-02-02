"""CEDAR Element Generator - Create CEDAR TemplateElements from openMINDS schemas."""

import re
import uuid
from datetime import datetime, timezone

import openminds.latest as om

from ..converters import Resolver
from ..registry import Registry


# Shared JSON-LD context for CEDAR elements and fields
BASE_CONTEXT = {
    "xsd": "http://www.w3.org/2001/XMLSchema#",
    "pav": "http://purl.org/pav/",
    "bibo": "http://purl.org/ontology/bibo/",
    "oslc": "http://open-services.net/ns/core#",
    "schema": "http://schema.org/",
    "skos": "http://www.w3.org/2004/02/skos/core#",
    "openminds": "https://openminds.om-i.org/vocab/",
    "schema:name": {"@type": "xsd:string"},
    "schema:description": {"@type": "xsd:string"},
    "pav:createdOn": {"@type": "xsd:dateTime"},
    "pav:createdBy": {"@type": "@id"},
    "pav:lastUpdatedOn": {"@type": "xsd:dateTime"},
    "oslc:modifiedBy": {"@type": "@id"},
}

# CEDAR metadata fields (null = set by CEDAR on upload)
CEDAR_METADATA = {
    "schema:schemaVersion": "1.6.0",
    "pav:version": "0.0.1",
    "pav:createdOn": None,
    "pav:createdBy": None,
    "pav:lastUpdatedOn": None,
    "oslc:modifiedBy": None,
    "bibo:status": "bibo:draft",
}


def snake_to_title(name: str) -> str:
    """Convert snake_case to Title Case."""
    return name.replace("_", " ").title()


class CEDARElementGenerator:
    """Generate CEDAR TemplateElements from openMINDS schemas."""

    def __init__(self, registry: Registry | None = None, resolver: Resolver | None = None):
        self.registry = registry or Registry()
        self.resolver = resolver or Resolver()

    def generate(self, schema_path: str) -> dict:
        """Generate CEDAR element for an openMINDS schema (e.g., 'core.Subject')."""
        om_class = self._resolve_schema(schema_path)
        name = om_class.__name__

        element = {
            "$schema": "http://json-schema.org/draft-04/schema#",
            "@type": "https://schema.metadatacenter.org/core/TemplateElement",
            "@id": f"urn:openminds2cedar:element:{schema_path}",
            "type": "object",
            "title": f"{name} element schema",
            "description": om_class.__doc__ or f"{name} from openMINDS",
            "schema:name": name.lower(),
            "schema:description": om_class.__doc__ or "",
            **CEDAR_METADATA,
            # openMINDS versioning
            "openminds:schemaVersion": self.registry.openminds_version,
            "openminds:generatedAt": datetime.now(timezone.utc).isoformat(),
            "openminds:sourceType": om_class.type_,
            # Structure
            "@context": {k: v for k, v in BASE_CONTEXT.items() if k != "skos"},
            "properties": self._create_properties(om_class),
            "_ui": {"order": [], "propertyLabels": {}, "propertyDescriptions": {}},
            "required": ["@context", "@id"],
            "additionalProperties": False,
        }

        # Populate UI and required from properties (use prop.name for snake_case)
        for prop in om_class.properties:
            element["_ui"]["order"].append(prop.name)
            element["_ui"]["propertyLabels"][prop.name] = snake_to_title(prop.name)
            element["_ui"]["propertyDescriptions"][prop.name] = prop.description or ""
            if prop.required:
                element["required"].append(prop.name)

        return element

    def _resolve_schema(self, path: str):
        """Resolve 'core.Subject' -> om.core.Subject."""
        obj = om
        for part in path.split("."):
            obj = getattr(obj, part, None)
            if obj is None:
                raise ValueError(f"Cannot resolve schema '{path}'")
        return obj

    def _create_properties(self, om_class) -> dict:
        """Create CEDAR properties from openMINDS class."""
        props = {
            "@context": {"type": "object", "properties": {}, "additionalProperties": False},
            "@id": {"type": "string", "format": "uri"},
            "@type": {
                "oneOf": [
                    {"type": "string", "format": "uri"},
                    {"type": "array", "minItems": 1, "items": {"type": "string", "format": "uri"}, "uniqueItems": True},
                ]
            },
        }
        for prop in om_class.properties:
            props[prop.name] = self._create_field(prop)
        return props

    def _create_field(self, prop) -> dict:
        """Create a CEDAR field from an openMINDS property."""
        field = {
            "$schema": "http://json-schema.org/draft-04/schema#",
            "@type": "https://schema.metadatacenter.org/core/TemplateField",
            "@id": f"https://repo.metadatacenter.org/template-fields/{uuid.uuid4()}",
            "@context": {**BASE_CONTEXT, "skos:prefLabel": {"@type": "xsd:string"}, "skos:altLabel": {"@type": "xsd:string"}},
            "type": "object",
            "title": f"{prop.name} field schema",
            "description": prop.description or f"{prop.name} field",
            "schema:name": prop.name,
            "schema:description": prop.description or "",
            "skos:prefLabel": snake_to_title(prop.name),
            **CEDAR_METADATA,
            "_ui": {"inputType": "textfield"},
            "_valueConstraints": {"requiredValue": prop.required},
            "additionalProperties": False,
            "properties": {
                "@type": {
                    "oneOf": [
                        {"type": "string", "format": "uri"},
                        {"type": "array", "minItems": 1, "items": {"type": "string", "format": "uri"}, "uniqueItems": True},
                    ]
                },
                "@value": {"type": ["string", "null"]},
                "rdfs:label": {"type": ["string", "null"]},
            },
        }

        if prop.required:
            field["required"] = ["@value"]

        # Check for controlled term via registry (use prop.name for snake_case lookup)
        if self.registry.has_field(prop.name):
            field_config = self.registry.field(prop.name)
            if "term_class" in field_config:
                self._add_controlled_term(field, field_config["term_class"], prop.multiple)

        return field

    def _add_controlled_term(self, field: dict, term_class: str, multiple: bool) -> None:
        """Add controlled term options to field."""
        options = self.resolver.get_options(term_class)
        count = len(options)

        # UI selection based on count
        if multiple:
            field["_ui"]["inputType"] = "checkbox"
        elif count <= 3:
            field["_ui"]["inputType"] = "radio"
        elif count <= 10:
            field["_ui"]["inputType"] = "list"
        else:
            field["_ui"]["inputType"] = "textfield"

        field["_valueConstraints"]["literals"] = [{"label": o["label"]} for o in options]
        field["_valueConstraints"]["multipleChoice"] = multiple
