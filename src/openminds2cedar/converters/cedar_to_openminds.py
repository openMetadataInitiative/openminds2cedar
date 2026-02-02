"""Convert CEDAR instances to openMINDS collections."""

import json
from pathlib import Path

import openminds.latest as om
from openminds import Collection

from .resolver import Resolver


class CEDARToOpenMINDSConverter:
    """Convert CEDAR instances to openMINDS Collection."""

    def __init__(self, resolver: Resolver | None = None):
        self.resolver = resolver or Resolver()

    def convert(self, instance_path: str | Path) -> Collection:
        """Convert a CEDAR instance JSON file to openMINDS Collection."""
        with open(instance_path) as f:
            return self.convert_instance(json.load(f))

    def convert_instance(self, instance: dict) -> Collection:
        """Convert a CEDAR instance dict to openMINDS Collection."""
        collection = Collection()

        subject_state = None
        if subjectstate_data := instance.get("subjectstate"):
            subject_state = self._convert_subject_state(subjectstate_data)
            collection.add(subject_state)

        if subject_data := instance.get("subject"):
            collection.add(self._convert_subject(subject_data, subject_state))

        return collection

    def _convert_subject(self, data: dict, subject_state=None) -> om.core.Subject:
        """Convert subject element to openMINDS Subject."""
        return om.core.Subject(
            species=self._resolve_term(data, "species", om.controlled_terms.Species),
            biological_sex=self._resolve_term(data, "biologicalSex", om.controlled_terms.BiologicalSex),
            internal_identifier=self._get_value(data, "internalIdentifier"),
            lookup_label=self._get_value(data, "lookupLabel"),
            studied_states=[subject_state] if subject_state else None,
        )

    def _convert_subject_state(self, data: dict) -> om.core.SubjectState:
        """Convert subjectstate element to openMINDS SubjectState."""
        return om.core.SubjectState(
            age_category=self._resolve_term(data, "ageCategory", om.controlled_terms.AgeCategory),
            handedness=self._resolve_term(data, "handedness", om.controlled_terms.Handedness),
            internal_identifier=self._get_value(data, "internalIdentifier"),
            lookup_label=self._get_value(data, "lookupLabel"),
            additional_remarks=self._get_value(data, "additionalRemarks"),
        )

    def _get_value(self, data: dict, field: str) -> str | None:
        """Extract value from CEDAR field structure."""
        if field_data := data.get(field):
            if isinstance(field_data, dict):
                value = field_data.get("@value")
                if value and value != "null":
                    return value
        return None

    def _resolve_term(self, data: dict, field: str, term_class):
        """Resolve controlled term value to openMINDS instance."""
        if value := self._get_value(data, field):
            return term_class.by_name(value)
        return None
