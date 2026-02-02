"""Shared test fixtures for CEDAR-openMINDS conversion tests.

These fixtures are used by:
- tests/conftest.py (pytest fixtures)
- scripts/publish_test_resources.py (manual testing)
"""

# =============================================================================
# Mock data for element fields (snake_case matching openMINDS Python API)
# =============================================================================

MOCK_SUBJECT_DATA = {
    "biological_sex": "male",
    "internal_identifier": "sub-mouse01",
    "lookup_label": "Mouse 01",
    "species": "Mus musculus",
}

MOCK_SUBJECTSTATE_DATA = {
    "age_category": "adult",
    "internal_identifier": "ses-01",
    "lookup_label": "Baseline Recording",
}

MOCK_PERSON_DATA = {
    "given_name": "John",
    "family_name": "Doe",
}

MOCK_TISSUESAMPLE_DATA = {
    "type": "tissue block",
    "origin": "brain",
    "species": "Mus musculus",
    "internal_identifier": "sample-001",
    "lookup_label": "Test Sample",
}

MOCK_TISSUESAMPLESTATE_DATA = {
    "internal_identifier": "state-001",
}


# =============================================================================
# Complete CEDAR instance structures (for converter tests)
# =============================================================================

def sample_cedar_instance():
    """A complete CEDAR instance with subject and subjectstate."""
    return {
        "@context": {
            "subject": "https://openminds.om-i.org/types/Subject",
            "subjectstate": "https://openminds.om-i.org/types/SubjectState",
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


def instance_with_nulls():
    """A minimal instance with null values to test edge cases."""
    return {
        "@context": {
            "subject": "https://openminds.om-i.org/types/Subject",
            "subjectstate": "https://openminds.om-i.org/types/SubjectState",
        },
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


def person_instance():
    """CEDAR instance for Person conversion test."""
    return {
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


def tissue_sample_instance():
    """CEDAR instance for TissueSample conversion test."""
    return {
        "@context": {
            "tissuesample": "https://openminds.om-i.org/types/TissueSample",
            "tissuesamplestate": "https://openminds.om-i.org/types/TissueSampleState",
        },
        "tissuesample": {
            "@context": {},
            "@id": "https://example.org/sample/1",
            "type": {"@value": "tissue block"},
            "origin": {"@value": "brain"},
            "species": {"@value": "Mus musculus"},
            "internal_identifier": {"@value": "sample-001"},
            "lookup_label": {"@value": "Test Sample"},
        },
        "tissuesamplestate": {
            "@context": {},
            "@id": "https://example.org/samplestate/1",
            "internal_identifier": {"@value": "state-001"},
        },
    }
