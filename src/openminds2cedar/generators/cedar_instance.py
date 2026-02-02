"""CEDAR instance generator from templates."""

from datetime import datetime, timezone


def _text_value(val: str | None) -> dict:
    """Create text field value structure."""
    return {"@value": val if val else None}


def _build_element_context(element: dict) -> dict:
    """Extract field->IRI mappings from element properties for @context."""
    ctx = {}
    for field_name, field_def in element.get("properties", {}).items():
        if field_name.startswith("@"):
            continue
        # Use openMINDS property URI if available, otherwise schema.org
        prop_uri = field_def.get("@context", {}).get("openminds:propertyId")
        if not prop_uri:
            prop_uri = f"https://openminds.om-i.org/props/{field_name}"
        ctx[field_name] = prop_uri
    return ctx


def _build_element_data(element: dict, data: dict) -> dict:
    """Build element instance data from template element and values."""
    result = {
        "@context": {},  # Empty context for element instances
        "@id": "https://repo.metadatacenter.org/.tmp",  # Temp URI, CEDAR assigns real ID
    }

    for field_name in element.get("_ui", {}).get("order", []):
        field_def = element.get("properties", {}).get(field_name)
        if not field_def:
            continue
        result[field_name] = _text_value(data.get(field_name))

    return result


def create_instance_payload(
    template: dict,
    name: str,
    description: str,
    subject_data: dict,
    subjectstate_data: dict,
    template_id: str | None = None,
) -> dict:
    """Create CEDAR instance payload from template and data.

    Args:
        template: CEDAR template schema
        name: Instance name
        description: Instance description
        subject_data: Dict of field_name -> value for subject element
        subjectstate_data: Dict of field_name -> value for subjectstate element
        template_id: CEDAR template ID (uses local URN if not provided)

    Returns:
        CEDAR instance JSON-LD payload
    """
    now = datetime.now(timezone.utc).isoformat()

    # Use provided template ID or the one from template
    # Clear local URN IDs - they don't work for validation
    schema_based_on = template_id or template.get("@id")
    if schema_based_on and schema_based_on.startswith("urn:"):
        schema_based_on = None

    # Build instance @context - merge element contexts into root
    # Handle both single elements and array elements (multiple: true)
    subject_prop = template.get("properties", {}).get("subject", {})
    subjectstate_prop = template.get("properties", {}).get("subjectstate", {})

    # Extract actual element (unwrap from array if needed)
    subject_element = subject_prop.get("items", subject_prop) if subject_prop.get("type") == "array" else subject_prop
    subjectstate_element = subjectstate_prop.get("items", subjectstate_prop) if subjectstate_prop.get("type") == "array" else subjectstate_prop

    # Track which are arrays for instance building
    subject_is_array = subject_prop.get("type") == "array"
    subjectstate_is_array = subjectstate_prop.get("type") == "array"

    instance_context = {
        "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
        "xsd": "http://www.w3.org/2001/XMLSchema#",
        "pav": "http://purl.org/pav/",
        "schema": "http://schema.org/",
        "oslc": "http://open-services.net/ns/core#",
        "skos": "http://www.w3.org/2004/02/skos/core#",
        "rdfs:label": {"@type": "xsd:string"},
        "skos:notation": {"@type": "xsd:string"},
        "pav:derivedFrom": {"@type": "@id"},
        "pav:createdOn": {"@type": "xsd:dateTime"},
        "pav:createdBy": {"@type": "@id"},
        "pav:lastUpdatedOn": {"@type": "xsd:dateTime"},
        "oslc:modifiedBy": {"@type": "@id"},
        "schema:isBasedOn": {"@type": "@id"},
        "schema:name": {"@type": "xsd:string"},
        "schema:description": {"@type": "xsd:string"},
        # Element type mappings
        "subject": subject_element.get("openminds:sourceType", "https://openminds.om-i.org/types/Subject"),
        "subjectstate": subjectstate_element.get("openminds:sourceType", "https://openminds.om-i.org/types/SubjectState"),
    }

    # Build element data, wrapping in array if element has multiple: true
    subject_instance = _build_element_data(subject_element, subject_data)
    subjectstate_instance = _build_element_data(subjectstate_element, subjectstate_data)

    return {
        "@context": instance_context,
        "@id": None,  # CEDAR assigns real ID on upload
        "schema:isBasedOn": schema_based_on,
        "schema:name": name,
        "schema:description": description,
        "pav:createdOn": now,
        "pav:lastUpdatedOn": now,
        "pav:createdBy": None,
        "oslc:modifiedBy": None,
        "subject": [subject_instance] if subject_is_array else subject_instance,
        "subjectstate": [subjectstate_instance] if subjectstate_is_array else subjectstate_instance,
    }


class CEDARInstanceGenerator:
    """Generate CEDAR instances from templates."""

    def __init__(self, template: dict, template_id: str | None = None):
        """Initialize with template.

        Args:
            template: CEDAR template schema dict
            template_id: Optional real CEDAR template ID (for published templates)
        """
        self.template = template
        self.template_id = template_id or template.get("@id")

    def create(
        self,
        name: str,
        description: str,
        subject_data: dict,
        subjectstate_data: dict,
    ) -> dict:
        """Create instance payload.

        Args:
            name: Instance name
            description: Instance description
            subject_data: Field values for subject element
            subjectstate_data: Field values for subjectstate element

        Returns:
            CEDAR instance JSON-LD payload
        """
        return create_instance_payload(
            self.template,
            name,
            description,
            subject_data,
            subjectstate_data,
            self.template_id,
        )
