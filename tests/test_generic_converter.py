"""Test generic CEDAR to openMINDS conversion."""

import pytest

from openminds2cedar.converters import CEDARToOpenMINDSConverter


def test_convert_subject_with_state_validates():
    """Test that converted Subject + SubjectState passes openMINDS validation."""
    instance = {
        "@context": {
            "subject": "https://openminds.om-i.org/types/Subject",
            "subjectstate": "https://openminds.om-i.org/types/SubjectState",
        },
        "subject": {
            "@context": {},
            "@id": "https://example.org/subject/1",
            "biological_sex": {"@value": "male"},
            "species": {"@value": "Mus musculus"},
            "internal_identifier": {"@value": "sub-001"},
            "lookup_label": {"@value": "Test Subject"},
        },
        "subjectstate": {
            "@context": {},
            "@id": "https://example.org/state/1",
            "age_category": {"@value": "adult"},
        },
    }

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


@pytest.mark.xfail(reason="Generic converter not yet implemented")
def test_convert_person_validates():
    """Test that converted Person passes openMINDS validation."""
    instance = {
        "@context": {
            "person": "https://openminds.om-i.org/types/Person",
        },
        "person": {
            "@context": {},
            "@id": "https://example.org/person/1",
            "given_name": {"@value": "John"},
            "family_name": {"@value": "Doe"},
        },
    }

    converter = CEDARToOpenMINDSConverter()
    collection = converter.convert_instance(instance)

    persons = [o for o in collection if type(o).__name__ == "Person"]
    assert len(persons) == 1, "Expected 1 Person"

    person = persons[0]
    assert person.given_name == "John"
    assert person.family_name == "Doe"

    failures = person.validate()
    assert not failures, f"Person validation failed: {failures}"


@pytest.mark.xfail(reason="Generic converter not yet implemented")
def test_convert_tissue_sample_validates():
    """Test that converted TissueSample passes openMINDS validation."""
    instance = {
        "@context": {
            "tissuesample": "https://openminds.om-i.org/types/TissueSample",
            "tissuesamplestate": "https://openminds.om-i.org/types/TissueSampleState",
        },
        "tissuesample": {
            "@context": {},
            "@id": "https://example.org/sample/1",
            "type": {"@value": "tissue sample"},
            "internal_identifier": {"@value": "sample-001"},
            "lookup_label": {"@value": "Test Sample"},
        },
        "tissuesamplestate": {
            "@context": {},
            "@id": "https://example.org/samplestate/1",
            "internal_identifier": {"@value": "state-001"},
        },
    }

    converter = CEDARToOpenMINDSConverter()
    collection = converter.convert_instance(instance)

    samples = [o for o in collection if type(o).__name__ == "TissueSample"]
    assert len(samples) == 1, "Expected 1 TissueSample"

    for obj in collection:
        failures = obj.validate()
        assert not failures, f"{type(obj).__name__} validation failed: {failures}"
