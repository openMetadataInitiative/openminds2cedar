"""Test CEDAR element and template generators."""


def test_generate_element(element_generator, registry):
    """Test element has correct structure, properties, UI, and metadata."""
    element = element_generator.generate("core.Subject")

    # Core structure
    assert element["@type"] == "https://schema.metadatacenter.org/core/TemplateElement"
    assert element["@id"] == "urn:openminds2cedar:element:core.Subject"
    assert element["schema:name"] == "subject"

    # Has properties from openMINDS schema
    assert "species" in element["properties"]
    assert "biologicalSex" in element["properties"]

    # Has UI configuration
    assert "order" in element["_ui"]
    assert "propertyLabels" in element["_ui"]

    # Has openMINDS metadata (from registry)
    assert element["openminds:schemaVersion"] == registry.openminds_version
    assert element["openminds:sourceType"] == "https://openminds.om-i.org/types/Subject"

    # Controlled term fields have value constraints (registry lookup)
    species_field = element["properties"]["species"]
    assert "_valueConstraints" in species_field
    assert "literals" in species_field["_valueConstraints"]
    assert len(species_field["_valueConstraints"]["literals"]) > 0


def test_generate_template(element_generator, template_generator):
    """Test template embeds elements with correct IDs."""
    subject = element_generator.generate("core.Subject")
    subjectstate = element_generator.generate("core.SubjectState")

    template = template_generator.generate(
        elements=[subject, subjectstate],
        element_ids=[subject["@id"], subjectstate["@id"]],
        name="test-template",
        description="Test template"
    )

    # Core structure
    assert template["@type"] == "https://schema.metadatacenter.org/core/Template"
    assert template["@id"] == "urn:openminds2cedar:template:test-template"

    # Elements embedded with preserved IDs
    assert "subject" in template["properties"]
    assert template["properties"]["subject"]["@id"] == "urn:openminds2cedar:element:core.Subject"
    assert template["properties"]["subjectstate"]["@id"] == "urn:openminds2cedar:element:core.SubjectState"


def test_generate_instance(generated_template, mock_subject_data, mock_subjectstate_data, converter):
    """Test instance creation, CEDAR validation, and openMINDS conversion."""
    from openminds2cedar.api import CEDARClient
    from openminds2cedar.generators import CEDARInstanceGenerator

    # Get published template ID from CEDAR
    client = CEDARClient()
    templates = client.list_folder(client.folders["templates"])
    template_id = next((t["@id"] for t in templates if t.get("schema:name") == "subject-study"), None)
    assert template_id, "Published template 'subject-study' not found"

    # Create instance with real template ID
    instance_gen = CEDARInstanceGenerator(generated_template, template_id=template_id)
    instance = instance_gen.create(
        name="Test_Mouse_01",
        description="Test instance",
        subject_data=mock_subject_data,
        subjectstate_data=mock_subjectstate_data,
    )

    # Has required CEDAR metadata
    assert instance["schema:name"] == "Test_Mouse_01"
    assert instance["schema:isBasedOn"] == template_id

    # Validate CEDAR instance via API
    result = client.validate(instance, "instance")
    assert result["valid"], f"CEDAR validation failed: {result['errors']}"

    # Convert to openMINDS and validate
    collection = converter.convert_instance(instance)
    for obj in collection:
        if hasattr(obj, "validate"):
            failures = obj.validate()
            assert not failures, f"openMINDS {type(obj).__name__} validation failed: {failures}"
