"""Test CEDAR template generation."""

import pytest


REGISTRY_TEMPLATES = ["subject-study", "tissue-sample-study", "dataset-metadata"]


@pytest.mark.parametrize("template_name", REGISTRY_TEMPLATES)
def test_template_from_registry(registry, element_generator, template_generator, template_name):
    """Test template generation and validation from registry definition."""
    from openminds2cedar.api import CEDARClient

    tmpl_def = registry.template(template_name)

    elements = [element_generator.generate(s) for s in tmpl_def["elements"]]
    element_ids = [e["@id"] for e in elements]

    template = template_generator.generate(
        elements, element_ids, template_name, tmpl_def.get("description", "")
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


def test_instance_workflow(generated_template, mock_subject_data, mock_subjectstate_data, converter):
    """Test instance creation, CEDAR validation, and openMINDS conversion."""
    from openminds2cedar.api import CEDARClient
    from openminds2cedar.generators import CEDARInstanceGenerator

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
