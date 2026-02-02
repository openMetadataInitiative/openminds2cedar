"""Test CEDAR template generation."""

import pytest

from openminds2cedar.api import CEDARClient
from openminds2cedar.generators import CEDARInstanceGenerator


REGISTRY_TEMPLATES = ["subject-study", "tissue-sample-study", "dataset-metadata"]


@pytest.mark.parametrize("template_name", REGISTRY_TEMPLATES)
def test_template_from_registry(registry, element_generator, template_generator, template_name):
    """Test template generation and validation from registry definition."""
    tmpl_def = registry.template(template_name)

    elements = []
    element_ids = []
    cardinalities = []
    for elem_def in tmpl_def["elements"]:
        schema = elem_def["schema"]
        multiple = elem_def.get("multiple", False)
        elem = element_generator.generate(schema)
        elements.append(elem)
        element_ids.append(elem["@id"])
        cardinalities.append(multiple)

    name = tmpl_def.get("name", template_name)
    template = template_generator.generate(
        elements, element_ids, name, tmpl_def.get("description", ""), cardinalities
    )

    assert template["@type"] == "https://schema.metadatacenter.org/core/Template"

    client = CEDARClient()
    result = client.validate_template(template)
    assert result["valid"], f"Template {template_name} validation failed: {result['errors']}"


def test_template_structure(element_generator, template_generator):
    """Test template embeds elements with correct IDs."""
    subject = element_generator.generate("core.Subject")
    subjectstate = element_generator.generate("core.SubjectState")

    template = template_generator.generate(
        elements=[subject, subjectstate],
        element_ids=[subject["@id"], subjectstate["@id"]],
        name="test-template",
        description="Test template"
    )

    assert template["@type"] == "https://schema.metadatacenter.org/core/Template"
    assert template["@id"] == "urn:openminds2cedar:template:test-template"
    assert "subject" in template["properties"]
    assert template["properties"]["subject"]["@id"] == "urn:openminds2cedar:element:core.Subject"


def test_template_cardinality(element_generator, template_generator):
    """Test cardinality: single vs multiple element structure."""
    subject = element_generator.generate("core.Subject")
    subjectstate = element_generator.generate("core.SubjectState")

    template = template_generator.generate(
        elements=[subject, subjectstate],
        element_ids=[subject["@id"], subjectstate["@id"]],
        name="test-cardinality",
        description="Test cardinality",
        cardinalities=[False, True],  # subject=single, subjectstate=multiple
    )

    # Single element: embedded directly
    assert template["properties"]["subject"]["@id"] == subject["@id"]
    assert "type" not in template["properties"]["subject"] or template["properties"]["subject"].get("type") != "array"

    # Multiple element: wrapped in array
    assert template["properties"]["subjectstate"]["type"] == "array"
    assert template["properties"]["subjectstate"]["minItems"] == 0
    assert template["properties"]["subjectstate"]["items"]["@id"] == subjectstate["@id"]


def test_instance_workflow(generated_template, mock_subject_data, mock_subjectstate_data, converter):
    """Test instance creation, CEDAR validation, and openMINDS conversion."""
    client = CEDARClient()
    templates = client.list_folder(client.folders["templates"])
    template_id = next((t["@id"] for t in templates if t.get("schema:name") == "subject-study"), None)
    assert template_id, "Published template 'subject-study' not found"

    instance_gen = CEDARInstanceGenerator(generated_template, template_id=template_id)
    instance = instance_gen.create(
        name="Test_Mouse_01",
        description="Test instance",
        subject_data=mock_subject_data,
        subjectstate_data=mock_subjectstate_data,
    )

    assert instance["schema:name"] == "Test_Mouse_01"

    result = client.validate(instance, "instance")
    assert result["valid"], f"CEDAR validation failed: {result['errors']}"

    collection = converter.convert_instance(instance)
    for obj in collection:
        if hasattr(obj, "validate"):
            failures = obj.validate()
            assert not failures, f"openMINDS {type(obj).__name__} validation failed: {failures}"
