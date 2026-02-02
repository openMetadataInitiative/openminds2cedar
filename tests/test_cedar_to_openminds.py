"""Test CEDAR to openMINDS converter."""

import json
import tempfile
from pathlib import Path

import pytest

from openminds2cedar.converters import CEDARToOpenMINDSConverter


# Sample CEDAR instance for testing
SAMPLE_INSTANCE = {
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


class TestCEDARToOpenMINDSConverter:
    """Test CEDAR to openMINDS conversion."""

    def test_convert_instance_creates_collection(self):
        """Test that convert_instance creates a Collection."""
        converter = CEDARToOpenMINDSConverter()
        collection = converter.convert_instance(SAMPLE_INSTANCE)

        # Should have objects in collection
        objects = list(collection)
        assert len(objects) > 0

    def test_convert_instance_creates_subject(self):
        """Test that converter creates Subject object."""
        converter = CEDARToOpenMINDSConverter()
        collection = converter.convert_instance(SAMPLE_INSTANCE)

        # Find Subject in collection
        subjects = [o for o in collection if type(o).__name__ == "Subject"]
        assert len(subjects) == 1

        subject = subjects[0]
        assert subject.internal_identifier == "sub-001"
        assert subject.lookup_label == "Test Subject"

    def test_convert_instance_creates_subject_state(self):
        """Test that converter creates SubjectState object."""
        converter = CEDARToOpenMINDSConverter()
        collection = converter.convert_instance(SAMPLE_INSTANCE)

        # Find SubjectState in collection
        states = [o for o in collection if type(o).__name__ == "SubjectState"]
        assert len(states) == 1

        state = states[0]
        assert state.internal_identifier == "ses-001"
        assert state.lookup_label == "Test Session"
        assert state.additional_remarks == "Test remarks"

    def test_convert_instance_resolves_species(self):
        """Test that species is resolved to openMINDS instance."""
        converter = CEDARToOpenMINDSConverter()
        collection = converter.convert_instance(SAMPLE_INSTANCE)

        subjects = [o for o in collection if type(o).__name__ == "Subject"]
        subject = subjects[0]

        assert subject.species is not None
        assert subject.species.name == "Mus musculus"

    def test_convert_instance_resolves_biological_sex(self):
        """Test that biologicalSex is resolved to openMINDS instance."""
        converter = CEDARToOpenMINDSConverter()
        collection = converter.convert_instance(SAMPLE_INSTANCE)

        subjects = [o for o in collection if type(o).__name__ == "Subject"]
        subject = subjects[0]

        assert subject.biological_sex is not None
        assert subject.biological_sex.name == "male"

    def test_convert_instance_resolves_age_category(self):
        """Test that ageCategory is resolved to openMINDS instance."""
        converter = CEDARToOpenMINDSConverter()
        collection = converter.convert_instance(SAMPLE_INSTANCE)

        states = [o for o in collection if type(o).__name__ == "SubjectState"]
        state = states[0]

        assert state.age_category is not None
        assert state.age_category.name == "adult"

    def test_convert_instance_links_subject_to_state(self):
        """Test that Subject is linked to SubjectState."""
        converter = CEDARToOpenMINDSConverter()
        collection = converter.convert_instance(SAMPLE_INSTANCE)

        subjects = [o for o in collection if type(o).__name__ == "Subject"]
        subject = subjects[0]

        assert subject.studied_states is not None
        assert len(subject.studied_states) == 1
        assert type(subject.studied_states[0]).__name__ == "SubjectState"

    def test_convert_instance_validates(self):
        """Test that all converted objects validate."""
        converter = CEDARToOpenMINDSConverter()
        collection = converter.convert_instance(SAMPLE_INSTANCE)

        for obj in collection:
            if hasattr(obj, "validate"):
                failures = obj.validate()
                assert len(failures) == 0, f"{type(obj).__name__} validation failed: {failures}"

    def test_convert_from_file(self, tmp_path):
        """Test converting from a JSON file."""
        # Write sample instance to temp file
        instance_file = tmp_path / "test_instance.json"
        with open(instance_file, "w") as f:
            json.dump(SAMPLE_INSTANCE, f)

        converter = CEDARToOpenMINDSConverter()
        collection = converter.convert(instance_file)

        assert len(list(collection)) > 0

    def test_handles_null_values(self):
        """Test that converter handles null values gracefully."""
        instance = {
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

        converter = CEDARToOpenMINDSConverter()
        collection = converter.convert_instance(instance)

        subjects = [o for o in collection if type(o).__name__ == "Subject"]
        subject = subjects[0]

        # Should handle nulls gracefully
        assert subject.biological_sex is None
        assert subject.internal_identifier is None
        assert subject.lookup_label is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
