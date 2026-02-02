"""CEDAR Element Generator - Create CEDAR TemplateElements from openMINDS schemas."""

from datetime import datetime, timezone

import openminds.latest as om

from ..api import CEDARClient
from ..converters import Resolver
from ..registry import Registry


class CEDARElementGenerator:
    """Generate CEDAR TemplateElements from openMINDS schemas."""

    def __init__(
        self,
        registry: Registry | None = None,
        resolver: Resolver | None = None,
        client: CEDARClient | None = None,
    ):
        self.registry = registry or Registry()
        self.resolver = resolver or Resolver()
        self.client = client  # Optional - only needed for validation

    def generate(self, schema_path: str) -> dict:
        """
        Generate CEDAR element for an openMINDS schema.

        Args:
            schema_path: e.g., 'core.Subject' or 'core.SubjectState'

        Returns:
            CEDAR TemplateElement dict
        """
        om_class = self._resolve_schema(schema_path)
        name = om_class.__name__

        element = {
            "$schema": "http://json-schema.org/draft-04/schema#",
            "@type": "https://schema.metadatacenter.org/core/TemplateElement",
            "@id": None,
            "type": "object",
            "title": f"{name} element schema",
            "description": om_class.__doc__ or f"{name} from openMINDS",
            "schema:name": name.lower(),
            "schema:description": om_class.__doc__ or "",
            "schema:schemaVersion": "1.6.0",
            "pav:version": "0.0.1",
            "pav:createdOn": None,
            "pav:createdBy": None,
            "pav:lastUpdatedOn": None,
            "oslc:modifiedBy": None,
            "bibo:status": "bibo:draft",
            # Versioning metadata
            "openminds:schemaVersion": self.registry.openminds_version,
            "openminds:generatedAt": datetime.now(timezone.utc).isoformat(),
            "openminds:sourceType": om_class.type_,
            # Structure
            "@context": self._create_context(),
            "properties": self._create_properties(om_class),
            "_ui": {"order": [], "propertyLabels": {}, "propertyDescriptions": {}},
            "required": ["@context", "@id"],
            "additionalProperties": False,
        }

        # Populate UI and required from properties
        for prop in om_class.properties:
            field_name = prop.path  # camelCase for JSON-LD
            element["_ui"]["order"].append(field_name)
            element["_ui"]["propertyLabels"][field_name] = self._to_label(field_name)
            element["_ui"]["propertyDescriptions"][field_name] = prop.description or ""
            if prop.required:
                element["required"].append(field_name)

        return element

    def generate_and_validate(self, schema_path: str) -> dict:
        """
        Generate and validate a CEDAR element.

        Raises ValueError if validation fails.
        """
        if not self.client:
            raise ValueError("CEDARClient required for validation. Pass client to constructor.")

        element = self.generate(schema_path)
        result = self.client.validate(element)

        if not result["valid"]:
            raise ValueError(f"CEDAR validation failed: {result['errors']}")

        return element

    def _resolve_schema(self, path: str):
        """Resolve 'core.Subject' -> om.core.Subject."""
        obj = om
        for part in path.split("."):
            obj = getattr(obj, part, None)
            if obj is None:
                raise ValueError(f"Cannot resolve schema '{path}'")
        return obj

    def _create_context(self) -> dict:
        """Create @context for element."""
        return {
            "xsd": "http://www.w3.org/2001/XMLSchema#",
            "pav": "http://purl.org/pav/",
            "bibo": "http://purl.org/ontology/bibo/",
            "oslc": "http://open-services.net/ns/core#",
            "schema": "http://schema.org/",
            "openminds": "https://openminds.om-i.org/vocab/",
            "schema:name": {"@type": "xsd:string"},
            "schema:description": {"@type": "xsd:string"},
            "pav:createdOn": {"@type": "xsd:dateTime"},
            "pav:createdBy": {"@type": "@id"},
            "pav:lastUpdatedOn": {"@type": "xsd:dateTime"},
            "oslc:modifiedBy": {"@type": "@id"},
        }

    def _create_field_context(self) -> dict:
        """Create @context for field."""
        return {
            "xsd": "http://www.w3.org/2001/XMLSchema#",
            "pav": "http://purl.org/pav/",
            "bibo": "http://purl.org/ontology/bibo/",
            "oslc": "http://open-services.net/ns/core#",
            "schema": "http://schema.org/",
            "skos": "http://www.w3.org/2004/02/skos/core#",
            "openminds": "https://openminds.om-i.org/vocab/",
            "schema:name": {"@type": "xsd:string"},
            "schema:description": {"@type": "xsd:string"},
            "skos:prefLabel": {"@type": "xsd:string"},
            "skos:altLabel": {"@type": "xsd:string"},
            "pav:createdOn": {"@type": "xsd:dateTime"},
            "pav:createdBy": {"@type": "@id"},
            "pav:lastUpdatedOn": {"@type": "xsd:dateTime"},
            "oslc:modifiedBy": {"@type": "@id"},
        }

    def _create_properties(self, om_class) -> dict:
        """Create CEDAR properties from openMINDS class."""
        props = {
            # Note: Omit 'required' key if empty - JSON Schema requires non-empty array
            "@context": {
                "type": "object",
                "properties": {},
                "additionalProperties": False,
            },
            "@id": {"type": "string", "format": "uri"},
            "@type": {
                "oneOf": [
                    {"type": "string", "format": "uri"},
                    {"type": "array", "minItems": 1, "items": {"type": "string", "format": "uri"}, "uniqueItems": True},
                ]
            },
        }

        for prop in om_class.properties:
            props[prop.path] = self._create_field(prop)

        return props

    def _create_field(self, prop) -> dict:
        """Create a CEDAR field from an openMINDS property."""
        import uuid
        import re

        field_name = prop.path  # camelCase for JSON-LD
        pref_label = re.sub(r"([A-Z])", r" \1", field_name).strip().title()

        field = {
            "$schema": "http://json-schema.org/draft-04/schema#",
            "@type": "https://schema.metadatacenter.org/core/TemplateField",
            "@id": f"https://repo.metadatacenter.org/template-fields/{uuid.uuid4()}",
            "@context": self._create_field_context(),
            "type": "object",
            "title": f"{field_name} field schema",
            "description": prop.description or f"{field_name} field",
            "schema:name": field_name,
            "schema:description": prop.description or "",
            "schema:schemaVersion": "1.6.0",
            "skos:prefLabel": pref_label,
            "pav:createdOn": None,
            "pav:createdBy": None,
            "pav:lastUpdatedOn": None,
            "oslc:modifiedBy": None,
            "_ui": {},
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

        # Add required array only if field is required
        if prop.required:
            field["required"] = ["@value"]

        # Check if controlled term via registry
        if self.registry.has_field(field_name):
            field_config = self.registry.field(field_name)
            if "term_class" in field_config:
                self._add_controlled_term(field, field_config["term_class"], prop.multiple)
                return field

        # Default to text field
        field["_ui"]["inputType"] = "textfield"
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

    def _to_label(self, name: str) -> str:
        """Convert camelCase to Title Case."""
        import re
        words = re.sub(r"([a-z])([A-Z])", r"\1 \2", name)
        return words.title()
