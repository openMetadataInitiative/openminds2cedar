"""Test generic CEDAR to openMINDS conversion."""

from openminds2cedar.converters import CEDARToOpenMINDSConverter
from tests.fixtures import (
    sample_cedar_instance,
    person_instance,
    tissue_sample_instance,
)


def test_convert_subject_with_state_validates():
    """Test that converted Subject + SubjectState passes openMINDS validation."""
    instance = sample_cedar_instance()

    converter = CEDARToOpenMINDSConverter()
    collection = converter.convert_instance(instance)

    subjects = [o for o in collection if type(o).__name__ == "Subject"]
    states = [o for o in collection if type(o).__name__ == "SubjectState"]
    assert len(subjects) == 1, "Expected 1 Subject"
    assert len(states) == 1, "Expected 1 SubjectState"

    # Subject should be linked to SubjectState
    assert subjects[0].studied_states is not None
    assert subjects[0].studied_states[0] is states[0]

    # Both should validate
    for obj in collection:
        failures = obj.validate()
        assert not failures, f"{type(obj).__name__} validation failed: {failures}"


def test_convert_person_validates():
    """Test that converted Person passes openMINDS validation."""
    instance = person_instance()

    converter = CEDARToOpenMINDSConverter()
    collection = converter.convert_instance(instance)

    persons = [o for o in collection if type(o).__name__ == "Person"]
    assert len(persons) == 1, "Expected 1 Person"

    person = persons[0]
    assert person.given_name == "John"
    assert person.family_name == "Doe"

    failures = person.validate()
    assert not failures, f"Person validation failed: {failures}"


def test_convert_tissue_sample_validates():
    """Test that converted TissueSample passes openMINDS validation."""
    instance = tissue_sample_instance()

    converter = CEDARToOpenMINDSConverter()
    collection = converter.convert_instance(instance)

    samples = [o for o in collection if type(o).__name__ == "TissueSample"]
    states = [o for o in collection if type(o).__name__ == "TissueSampleState"]
    assert len(samples) == 1, "Expected 1 TissueSample"
    assert len(states) == 1, "Expected 1 TissueSampleState"

    # TissueSample should be linked to TissueSampleState
    assert samples[0].studied_states is not None
    assert samples[0].studied_states[0] is states[0]

    for obj in collection:
        failures = obj.validate()
        assert not failures, f"{type(obj).__name__} validation failed: {failures}"
