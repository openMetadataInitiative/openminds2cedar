"""Test CEDAR to openMINDS converter."""

import json


def test_convert_instance(converter, sample_cedar_instance_fixture):
    """Test conversion creates objects, resolves terms, and links them."""
    collection = converter.convert_instance(sample_cedar_instance_fixture)
    objects = list(collection)

    subjects = [o for o in objects if type(o).__name__ == "Subject"]
    states = [o for o in objects if type(o).__name__ == "SubjectState"]
    assert len(subjects) == 1
    assert len(states) == 1

    subject, state = subjects[0], states[0]

    # Resolves controlled terms
    assert subject.species.name == "Mus musculus"
    assert subject.biological_sex.name == "male"
    assert state.age_category.name == "adult"

    # Links Subject to SubjectState
    assert len(subject.studied_states) == 1
    assert subject.studied_states[0] is state


def test_convert_from_file(converter, sample_cedar_instance_fixture, tmp_path):
    """Test converting from a JSON file."""
    instance_file = tmp_path / "test_instance.json"
    instance_file.write_text(json.dumps(sample_cedar_instance_fixture))

    collection = converter.convert(instance_file)
    assert len(list(collection)) > 0


def test_converted_objects_validate(converter, sample_cedar_instance_fixture):
    """Test that converted objects pass openMINDS validation."""
    collection = converter.convert_instance(sample_cedar_instance_fixture)

    for obj in collection:
        if hasattr(obj, "validate"):
            failures = obj.validate()
            assert not failures, f"{type(obj).__name__} failed: {failures}"


def test_handles_null_values(converter, instance_with_nulls_fixture):
    """Test that null values are handled gracefully."""
    collection = converter.convert_instance(instance_with_nulls_fixture)

    subjects = [o for o in collection if type(o).__name__ == "Subject"]
    assert subjects[0].biological_sex is None
    assert subjects[0].internal_identifier is None
