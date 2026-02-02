"""Shared test fixtures."""

import pytest

from openminds2cedar.generators import (
    CEDARElementGenerator,
    CEDARTemplateGenerator,
    CEDARInstanceGenerator,
)
from openminds2cedar.converters import CEDARToOpenMINDSConverter
from openminds2cedar.registry import Registry

from tests.fixtures import (
    MOCK_SUBJECT_DATA,
    MOCK_SUBJECTSTATE_DATA,
    sample_cedar_instance,
    instance_with_nulls,
)


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
        name="subject-study",
        description="Subject with multiple states",
        cardinalities=[False, True],  # Subject=single, SubjectState=multiple
    )


@pytest.fixture
def instance_generator(generated_template):
    return CEDARInstanceGenerator(generated_template)


# --- Test Data (from shared fixtures) ---

@pytest.fixture
def mock_subject_data():
    """Mock data for a mouse subject (snake_case field names)."""
    return MOCK_SUBJECT_DATA.copy()


@pytest.fixture
def mock_subjectstate_data():
    """Mock data for subject state (snake_case field names)."""
    return MOCK_SUBJECTSTATE_DATA.copy()


@pytest.fixture
def sample_cedar_instance_fixture():
    """A complete CEDAR instance with subject and subjectstate (snake_case fields)."""
    return sample_cedar_instance()


@pytest.fixture
def instance_with_nulls_fixture():
    """A minimal instance with null values to test edge cases."""
    return instance_with_nulls()
