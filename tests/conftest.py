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
    """A complete generated template with Subject and SubjectState elements."""
    subject = element_generator.generate("core.Subject")
    subjectstate = element_generator.generate("core.SubjectState")
    return template_generator.generate(
        elements=[subject, subjectstate],
        element_ids=[subject["@id"], subjectstate["@id"]],
        name="subject-study",
        description="Test template"
    )


@pytest.fixture
def instance_generator(generated_template):
    return CEDARInstanceGenerator(generated_template)


@pytest.fixture
def mock_subject_data():
    """Mock data for a mouse subject."""
    return {
        "biologicalSex": "male",
        "internalIdentifier": "sub-mouse01",
        "lookupLabel": "Mouse 01",
        "species": "Mus musculus",
        "studiedState": "baseline",
    }


@pytest.fixture
def mock_subjectstate_data():
    """Mock data for subject state."""
    return {
        "ageCategory": "adult",
        "internalIdentifier": "ses-01",
        "lookupLabel": "Baseline Recording",
    }


# --- Test Data ---

@pytest.fixture
def sample_cedar_instance():
    """A complete CEDAR instance with subject and subjectstate."""
    return {
        "@context": {
            "subject": "https://openminds.om-i.org/types/Subject",
            "subjectstate": "https://openminds.om-i.org/types/SubjectState"
        },
        "schema:name": "Test_Instance",
        "subject": {
            "@context": {},
            "@id": "https://example.org/subject/1",
            "biologicalSex": {"@value": "male"},
            "internalIdentifier": {"@value": "sub-001"},
            "lookupLabel": {"@value": "Test Subject"},
            "species": {"@value": "Mus musculus"},
            "studiedState": {"@value": "baseline"},
            "isPartOf": {"@value": None},
        },
        "subjectstate": {
            "@context": {},
            "@id": "https://example.org/subjectstate/1",
            "ageCategory": {"@value": "adult"},
            "handedness": {"@value": None},
            "internalIdentifier": {"@value": "ses-001"},
            "lookupLabel": {"@value": "Test Session"},
            "additionalRemarks": {"@value": "Test remarks"},
            "age": {"@value": None},
            "weight": {"@value": None},
            "attribute": {"@value": None},
            "descendedFrom": {"@value": None},
            "pathology": {"@value": None},
            "relativeTimeIndication": {"@value": None},
        },
    }


@pytest.fixture
def instance_with_nulls():
    """A minimal instance with null values to test edge cases."""
    return {
        "subject": {
            "@context": {},
            "@id": "https://example.org/subject/1",
            "biologicalSex": {"@value": None},
            "species": {"@value": "Mus musculus"},
            "internalIdentifier": {"@value": None},
            "lookupLabel": {"@value": None},
            "studiedState": {"@value": None},
            "isPartOf": {"@value": None},
        },
        "subjectstate": {
            "@context": {},
            "@id": "https://example.org/subjectstate/1",
            "ageCategory": {"@value": "adult"},
        },
    }
