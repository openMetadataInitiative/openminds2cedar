"""Shared test fixtures."""

import pytest

from openminds2cedar.generators import (
    CEDARElementGenerator,
    CEDARTemplateGenerator,
    CEDARInstanceGenerator,
)
from openminds2cedar.converters import CEDARToOpenMINDSConverter
from openminds2cedar.registry import Registry


# --- Generators ---

@pytest.fixture
def registry():
    return Registry()


@pytest.fixture
def element_generator(registry):
    return CEDARElementGenerator(registry=registry)


@pytest.fixture
def template_generator():
    return CEDARTemplateGenerator()


@pytest.fixture
def converter():
    return CEDARToOpenMINDSConverter()


@pytest.fixture
def generated_template(element_generator, template_generator):
    """A complete generated template with Subject (single) and SubjectState (multiple)."""
    subject = element_generator.generate("core.Subject")
    subjectstate = element_generator.generate("core.SubjectState")
    return template_generator.generate(
        elements=[subject, subjectstate],
        element_ids=[subject["@id"], subjectstate["@id"]],
        name="1subject-Nstates",
        description="Test template with cardinality",
        cardinalities=[False, True],  # Subject=single, SubjectState=multiple
    )


@pytest.fixture
def instance_generator(generated_template):
    return CEDARInstanceGenerator(generated_template)


@pytest.fixture
def mock_subject_data():
    """Mock data for a mouse subject (snake_case field names)."""
    return {
        "biological_sex": "male",
        "internal_identifier": "sub-mouse01",
        "lookup_label": "Mouse 01",
        "species": "Mus musculus",
    }


@pytest.fixture
def mock_subjectstate_data():
    """Mock data for subject state (snake_case field names)."""
    return {
        "age_category": "adult",
        "internal_identifier": "ses-01",
        "lookup_label": "Baseline Recording",
    }


# --- Test Data ---

@pytest.fixture
def sample_cedar_instance():
    """A complete CEDAR instance with subject and subjectstate (snake_case fields)."""
    return {
        "@context": {
            "subject": "https://openminds.om-i.org/types/Subject",
            "subjectstate": "https://openminds.om-i.org/types/SubjectState"
        },
        "schema:name": "Test_Instance",
        "subject": {
            "@context": {},
            "@id": "https://example.org/subject/1",
            "biological_sex": {"@value": "male"},
            "internal_identifier": {"@value": "sub-001"},
            "lookup_label": {"@value": "Test Subject"},
            "species": {"@value": "Mus musculus"},
        },
        "subjectstate": {
            "@context": {},
            "@id": "https://example.org/subjectstate/1",
            "age_category": {"@value": "adult"},
            "handedness": {"@value": None},
            "internal_identifier": {"@value": "ses-001"},
            "lookup_label": {"@value": "Test Session"},
            "additional_remarks": {"@value": "Test remarks"},
        },
    }


@pytest.fixture
def instance_with_nulls():
    """A minimal instance with null values to test edge cases."""
    return {
        "subject": {
            "@context": {},
            "@id": "https://example.org/subject/1",
            "biological_sex": {"@value": None},
            "species": {"@value": "Mus musculus"},
            "internal_identifier": {"@value": None},
            "lookup_label": {"@value": None},
        },
        "subjectstate": {
            "@context": {},
            "@id": "https://example.org/subjectstate/1",
            "age_category": {"@value": "adult"},
        },
    }
