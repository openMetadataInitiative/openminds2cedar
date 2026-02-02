"""Test CEDAR element generation."""

import pytest


CORE_SCHEMAS = [
    "core.Subject",
    "core.SubjectState",
    "core.TissueSample",
    "core.TissueSampleState",
    "core.Dataset",
    "core.DatasetVersion",
    "core.Person",
    "core.Organization",
    "core.Software",
    "core.Protocol",
]


@pytest.mark.parametrize("schema", CORE_SCHEMAS)
def test_generate_core_elements(element_generator, schema):
    """Test element generation for core schemas."""
    element = element_generator.generate(schema)

    assert element["@type"] == "https://schema.metadatacenter.org/core/TemplateElement"
    assert element["@id"] == f"urn:openminds2cedar:element:{schema}"
    assert "properties" in element
    assert "_ui" in element
    assert len(element["_ui"]["order"]) > 0


@pytest.mark.parametrize("schema", CORE_SCHEMAS)
def test_elements_validate_via_cedar_api(element_generator, schema):
    """Test that generated elements validate via CEDAR API."""
    from openminds2cedar.api import CEDARClient

    client = CEDARClient()
    element = element_generator.generate(schema)

    result = client.validate(element, "element")
    assert result["valid"], f"CEDAR validation failed for {schema}: {result['errors']}"


def test_element_structure(element_generator, registry):
    """Test element has correct structure, properties, UI, and metadata."""
    element = element_generator.generate("core.Subject")

    # Core structure
    assert element["schema:name"] == "subject"
    assert element["openminds:schemaVersion"] == registry.openminds_version
    assert element["openminds:sourceType"] == "https://openminds.om-i.org/types/Subject"

    # Has properties from openMINDS schema
    assert "species" in element["properties"]
    assert "biologicalSex" in element["properties"]

    # Controlled term fields have value constraints
    species_field = element["properties"]["species"]
    assert "literals" in species_field["_valueConstraints"]
    assert len(species_field["_valueConstraints"]["literals"]) > 0
