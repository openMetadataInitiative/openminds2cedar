"""
CEDAR to openMINDS Converter.

Converts filled CEDAR instances to openMINDS Collection objects.

Usage:
    from openminds2cedar.converters import CEDARToOpenMINDSConverter

    converter = CEDARToOpenMINDSConverter()
    collection = converter.convert('data/cedar/instances/Mouse_C57BL6_Control_01.json')
    collection.save('output/')
"""

import json
from pathlib import Path

import openminds.latest as om
from openminds import Collection

from .resolver import Resolver
from ..registry import Registry


class CEDARToOpenMINDSConverter:
    """Convert CEDAR instances to openMINDS Collection."""

    def __init__(self, registry: Registry | None = None, resolver: Resolver | None = None):
        self.registry = registry or Registry()
        self.resolver = resolver or Resolver()

    def convert(self, instance_path: str | Path) -> Collection:
        """
        Convert a CEDAR instance JSON file to openMINDS Collection.

        Args:
            instance_path: Path to CEDAR instance JSON file

        Returns:
            openMINDS Collection with Subject and SubjectState objects
        """
        with open(instance_path) as f:
            instance = json.load(f)

        return self.convert_instance(instance)

    def convert_instance(self, instance: dict) -> Collection:
        """
        Convert a CEDAR instance dict to openMINDS Collection.

        Args:
            instance: CEDAR instance dict

        Returns:
            openMINDS Collection with converted objects
        """
        collection = Collection()

        # Extract elements from instance
        subject_data = instance.get("subject", {})
        subjectstate_data = instance.get("subjectstate", {})

        # Convert SubjectState first (Subject references it)
        subject_state = None
        if subjectstate_data:
            subject_state = self._convert_subject_state(subjectstate_data)
            collection.add(subject_state)

        # Convert Subject
        if subject_data:
            subject = self._convert_subject(subject_data, subject_state)
            collection.add(subject)

        return collection

    def _convert_subject(self, data: dict, subject_state=None) -> om.core.Subject:
        """Convert subject element data to openMINDS Subject."""
        # Resolve controlled terms
        species = self._resolve_controlled_term(data, "species", "controlled_terms.Species")
        biological_sex = self._resolve_controlled_term(data, "biologicalSex", "controlled_terms.BiologicalSex")

        # Get text fields
        internal_id = self._get_value(data, "internalIdentifier")
        lookup_label = self._get_value(data, "lookupLabel")

        # Create Subject
        subject = om.core.Subject(
            species=species,
            biological_sex=biological_sex,
            internal_identifier=internal_id,
            lookup_label=lookup_label,
            studied_states=[subject_state] if subject_state else None,
        )

        return subject

    def _convert_subject_state(self, data: dict) -> om.core.SubjectState:
        """Convert subjectstate element data to openMINDS SubjectState."""
        # Resolve controlled terms
        age_category = self._resolve_controlled_term(data, "ageCategory", "controlled_terms.AgeCategory")
        handedness = self._resolve_controlled_term(data, "handedness", "controlled_terms.Handedness")

        # Get text fields
        internal_id = self._get_value(data, "internalIdentifier")
        lookup_label = self._get_value(data, "lookupLabel")
        additional_remarks = self._get_value(data, "additionalRemarks")

        # Create SubjectState
        subject_state = om.core.SubjectState(
            age_category=age_category,
            handedness=handedness,
            internal_identifier=internal_id,
            lookup_label=lookup_label,
            additional_remarks=additional_remarks,
        )

        return subject_state

    def _get_value(self, data: dict, field_name: str) -> str | None:
        """Extract value from CEDAR field structure."""
        field = data.get(field_name, {})
        if isinstance(field, dict):
            value = field.get("@value")
            if value and value != "null":
                return value
        return None

    def _resolve_controlled_term(self, data: dict, field_name: str, term_class_path: str):
        """Resolve controlled term value to openMINDS instance."""
        value = self._get_value(data, field_name)
        if not value:
            return None

        # Use resolver to get the openMINDS instance
        term_class = self.resolver.resolve_class(term_class_path)
        result = term_class.by_name(value)
        return result
