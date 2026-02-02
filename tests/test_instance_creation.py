"""
Test creating CEDAR instances from mock data and uploading via API.

Template: subject-test-2 (Subject + SubjectState elements)
ID: https://repo.metadatacenter.org/templates/a717ed35-b095-4395-b5a6-73d1e7d03443
"""

import json
import os
from datetime import datetime
from pathlib import Path

import pytest

from openminds2cedar.api.cedar_client import CEDARClient


# Template configuration
TEMPLATE_ID = "https://repo.metadatacenter.org/templates/a717ed35-b095-4395-b5a6-73d1e7d03443"

# Property URIs from template @context - using openMINDS type URIs
SUBJECT_IRI = "https://openminds.om-i.org/types/Subject"
SUBJECTSTATE_IRI = "https://openminds.om-i.org/types/SubjectState"


def value_or_null(val):
    """Return @value structure, using null for empty strings."""
    if val == "" or val is None:
        return {"@value": None}
    return {"@value": val}


def create_instance_payload(subject_data: dict, subjectstate_data: dict) -> dict:
    """
    Create a CEDAR instance JSON-LD payload for subject-test-2 template.

    Args:
        subject_data: Dict with subject fields (species, biologicalSex, etc.)
        subjectstate_data: Dict with subject state fields (ageCategory, etc.)

    Returns:
        Complete instance payload ready for CEDAR API
    """
    import uuid
    now = datetime.now().astimezone().isoformat()
    # Generate temp URIs for elements - CEDAR will replace with permanent IDs
    subject_temp_id = f"https://repo.metadatacenter.org/template-element-instances/{uuid.uuid4()}"
    subjectstate_temp_id = f"https://repo.metadatacenter.org/template-element-instances/{uuid.uuid4()}"

    instance = {
        "@context": {
            "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
            "xsd": "http://www.w3.org/2001/XMLSchema#",
            "pav": "http://purl.org/pav/",
            "schema": "http://schema.org/",
            "oslc": "http://open-services.net/ns/core#",
            "skos": "http://www.w3.org/2004/02/skos/core#",
            "skos:notation": {"@type": "xsd:string"},
            "pav:derivedFrom": {"@type": "@id"},
            "pav:createdOn": {"@type": "xsd:dateTime"},
            "pav:createdBy": {"@type": "@id"},
            "pav:lastUpdatedOn": {"@type": "xsd:dateTime"},
            "oslc:modifiedBy": {"@type": "@id"},
            "schema:isBasedOn": {"@type": "@id"},
            "rdfs:label": {"@type": "xsd:string"},
            "schema:description": {"@type": "xsd:string"},
            "schema:name": {"@type": "xsd:string"},
            "subject": SUBJECT_IRI,
            "subjectstate": SUBJECTSTATE_IRI,
        },
        "schema:isBasedOn": TEMPLATE_ID,
        "schema:name": subject_data.get("name", "Untitled Instance"),
        "schema:description": subject_data.get("description", ""),
        "pav:createdOn": now,
        "pav:lastUpdatedOn": now,
        # Subject element - use temp UUID URI (CEDAR assigns permanent ID)
        "subject": {
            "@context": {},
            "@id": subject_temp_id,
            "biologicalSex": value_or_null(subject_data.get("biologicalSex")),
            "internalIdentifier": value_or_null(subject_data.get("internalIdentifier")),
            "isPartOf": value_or_null(subject_data.get("isPartOf")),
            "lookupLabel": value_or_null(subject_data.get("lookupLabel")),
            "species": value_or_null(subject_data.get("species")),
            "studiedState": value_or_null(subject_data.get("studiedState")),
        },
        # SubjectState element - use temp UUID URI
        "subjectstate": {
            "@context": {},
            "@id": subjectstate_temp_id,
            "additionalRemarks": value_or_null(subjectstate_data.get("additionalRemarks")),
            "age": value_or_null(subjectstate_data.get("age")),
            "ageCategory": value_or_null(subjectstate_data.get("ageCategory")),
            "attribute": value_or_null(subjectstate_data.get("attribute")),
            "descendedFrom": value_or_null(subjectstate_data.get("descendedFrom")),
            "handedness": value_or_null(subjectstate_data.get("handedness")),
            "internalIdentifier": value_or_null(subjectstate_data.get("internalIdentifier")),
            "lookupLabel": value_or_null(subjectstate_data.get("lookupLabel")),
            "pathology": value_or_null(subjectstate_data.get("pathology")),
            "relativeTimeIndication": value_or_null(subjectstate_data.get("relativeTimeIndication")),
            "weight": value_or_null(subjectstate_data.get("weight")),
        },
    }

    return instance


# Mock data fixtures
MOUSE_SUBJECT = {
    "name": "Mouse_C57BL6_Control_01",
    "description": "C57BL/6J mouse - control group, baseline recording",
    "biologicalSex": "male",
    "internalIdentifier": "sub-mouse01",
    "isPartOf": "",
    "lookupLabel": "Mouse 01 - C57BL/6J Control",
    "species": "Mus musculus",
    "studiedState": "baseline",
}

MOUSE_STATE = {
    "additionalRemarks": "Good signal quality, normal behavior",
    "age": "90 days",
    "ageCategory": "adult",
    "attribute": "",
    "descendedFrom": "",
    "handedness": "",
    "internalIdentifier": "ses-baseline",
    "lookupLabel": "Mouse 01 - Baseline Session",
    "pathology": "",
    "relativeTimeIndication": "",
    "weight": "25.3 g",
}

NHP_SUBJECT = {
    "name": "Macaque_M1_Trained_Adult",
    "description": "Adult macaque with electrode implant - motor cortex study",
    "biologicalSex": "female",
    "internalIdentifier": "sub-monkey01",
    "isPartOf": "",
    "lookupLabel": "Macaque M1 - Trained Adult",
    "species": "Macaca mulatta",
    "studiedState": "trained",
}

NHP_STATE = {
    "additionalRemarks": "Fully trained on reach task, consistent performance",
    "age": "5.5 years",
    "ageCategory": "adult",
    "attribute": "",
    "descendedFrom": "",
    "handedness": "right handedness",
    "internalIdentifier": "ses-presurg",
    "lookupLabel": "M1 - Pre-Surgery Baseline",
    "pathology": "",
    "relativeTimeIndication": "",
    "weight": "6.2 kg",
}


class TestInstanceCreation:
    """Test CEDAR instance creation."""

    def test_create_instance_payload_structure(self):
        """Test that instance payload has correct structure."""
        payload = create_instance_payload(MOUSE_SUBJECT, MOUSE_STATE)

        # Check top-level structure
        assert "@context" in payload
        assert "schema:isBasedOn" in payload
        assert payload["schema:isBasedOn"] == TEMPLATE_ID
        assert "subject" in payload
        assert "subjectstate" in payload

        # Check element structure
        assert payload["subject"]["species"] == {"@value": "Mus musculus"}
        assert payload["subjectstate"]["ageCategory"] == {"@value": "adult"}

    def test_value_or_null_with_value(self):
        """Test value helper with actual value."""
        assert value_or_null("test") == {"@value": "test"}

    def test_value_or_null_with_empty(self):
        """Test value helper with empty string."""
        assert value_or_null("") == {"@value": None}

    def test_value_or_null_with_none(self):
        """Test value helper with None."""
        assert value_or_null(None) == {"@value": None}

    @pytest.mark.skipif(
        not os.getenv("CEDAR_API_KEY"),
        reason="CEDAR_API_KEY not set - skipping API test"
    )
    def test_upload_mouse_instance(self, tmp_path):
        """Test uploading mouse instance to CEDAR API."""
        client = CEDARClient()
        payload = create_instance_payload(MOUSE_SUBJECT, MOUSE_STATE)

        # Save payload for inspection
        payload_file = tmp_path / "mouse_instance.json"
        with open(payload_file, "w") as f:
            json.dump(payload, f, indent=2)
        print(f"Saved payload to {payload_file}")

        result = client.upload_instance(payload)
        print(f"Upload result: {result}")

        assert result["success"], f"Failed to upload: {result['error']}"
        assert result["id"] is not None
        print(f"Created instance: {result['id']}")

    @pytest.mark.skipif(
        not os.getenv("CEDAR_API_KEY"),
        reason="CEDAR_API_KEY not set - skipping API test"
    )
    def test_upload_nhp_instance(self, tmp_path):
        """Test uploading NHP instance to CEDAR API."""
        client = CEDARClient()
        payload = create_instance_payload(NHP_SUBJECT, NHP_STATE)

        # Save payload for inspection
        payload_file = tmp_path / "nhp_instance.json"
        with open(payload_file, "w") as f:
            json.dump(payload, f, indent=2)

        result = client.upload_instance(payload)
        print(f"Upload result: {result}")

        assert result["success"], f"Failed to upload: {result['error']}"
        assert result["id"] is not None
        print(f"Created instance: {result['id']}")


def run_all_uploads():
    """Run all instance uploads (for manual testing)."""
    client = CEDARClient()

    instances = [
        ("Mouse", MOUSE_SUBJECT, MOUSE_STATE),
        ("NHP", NHP_SUBJECT, NHP_STATE),
    ]

    # Save payloads to project tmp directory
    tmp_dir = Path(__file__).parent.parent / "tmp"
    tmp_dir.mkdir(exist_ok=True)

    created = []
    for name, subject, state in instances:
        print(f"Processing {name} instance...")
        payload = create_instance_payload(subject, state)

        # Save payload
        payload_file = tmp_dir / f"instance_{name.lower()}.json"
        with open(payload_file, "w") as f:
            json.dump(payload, f, indent=2)
        print(f"  Saved payload to {payload_file}")

        # Upload
        result = client.upload_instance(payload)
        if result["success"]:
            print(f"  Created: {result['id']}")
            created.append(result)
        else:
            print(f"  Failed: {result['error']}")

    print(f"\nCreated {len(created)}/{len(instances)} instances.")
    return created


if __name__ == "__main__":
    run_all_uploads()
