#!/usr/bin/env python3
"""
Controlled Terms Loader - Load openMINDS instances for CEDAR value lists

This module handles the integration of openMINDS controlled vocabularies into CEDAR
TemplateElements. It automatically detects available controlled terms, loads their
instances from the openMINDS_instances repository, and generates appropriate CEDAR
value constraints with user-friendly inputTypes.

Key Design Decisions:
1. Use literals (labels) rather than ontology classes for exact term control
2. Smart inputType selection based on number of options (radio vs list vs checkbox)
3. Load directly from openMINDS_instances to avoid external dependencies
4. Support flat format for backward compatibility with existing code

CEDAR inputType Selection Logic:
- Radio buttons (<=5 options): Best for small, fixed sets (e.g., biologicalSex)
- Dropdown list (>5 options): Best for larger sets (e.g., species with 25 options)
- Checkboxes (multiple=True): For multi-select scenarios

Quirks and Limitations:
- openMINDS IRIs not directly preserved in literal labels (future: see NEXT_STEPS.md)
- No dynamic updates from openMINDS (requires manual submodule update)
- Assumes openMINDS_instances directory structure is fixed
"""

import json
from pathlib import Path
from typing import List, Dict, Optional


class ControlledTermsLoader:
    """
    Load controlled term instances from openMINDS_instances and create CEDAR constraints

    This class bridges openMINDS controlled vocabularies and CEDAR value constraints,
    providing automatic detection and appropriate UI selection for controlled term fields.
    """

    def __init__(self, instances_path: str = "external/openMINDS_instances/instances/latest/terminologies"):
        """
        Initialize the controlled terms loader

        Args:
            instances_path: Path to openMINDS_instances terminologies directory

        Note: Assumes the directory structure:
            terminologies/
                biologicalSex/
                    female.jsonld
                    male.jsonld
                    ...
                species/
                    homoSapiens.jsonld
                    musMusculus.jsonld
                    ...
        """
        self.terminologies_path = Path(instances_path)

    def has_controlled_terms(self, field_name: str) -> bool:
        """
        Check if field has controlled term instances in openMINDS

        Args:
            field_name: Clean field name (e.g., 'biologicalSex', 'species')

        Returns:
            True if instances directory exists and contains JSONLD files

        Note: Field name must match openMINDS_instances directory name exactly.
              Case sensitive!
        """
        term_path = self.terminologies_path / field_name
        return term_path.exists() and any(term_path.glob("*.jsonld"))

    def get_cedar_value_constraints(self, field_name: str, is_required: bool = False,
                                   multiple: bool = False, flat_format: bool = False) -> Optional[Dict]:
        """
        Get CEDAR value constraints using literal-based approach with appropriate inputType

        Strategy:
        - Small lists (<= 5 items): Use radio buttons for single choice
        - Larger lists: Use dropdown (list inputType)
        - Always use literals from openMINDS instances for exact term control

        Args:
            field_name: Name of the field
            is_required: Whether the field is required
            multiple: Whether multiple values allowed
            flat_format: If True, return flat dict for backward compatibility

        Returns:
            Dict with 'inputType' and 'valueConstraints', or flat dict if flat_format=True
            Returns None if no instances exist
        """
        if not self.has_controlled_terms(field_name):
            return None

        instances = self.load_instances(field_name)
        if not instances:
            return None

        # Create literals from openMINDS instances
        literals = []
        for inst in instances:
            literal = {"label": inst["name"]}
            literals.append(literal)

        # DECISION POINT: Choose inputType based on UX best practices
        #
        # Rationale for thresholds:
        # - Radio buttons (<=5): Quick visual scanning, no clicks needed
        # - Dropdown list (>5): Saves screen space, supports search/scroll
        # - Checkboxes (multiple): Clear multi-select affordance
        #
        # Trade-off: Fixed threshold may not suit all contexts, but provides
        # consistent, predictable behavior across all schemas
        if len(literals) <= 5 and not multiple:
            # Small list: use radio buttons
            # Example: biologicalSex (4 options) - users can see all choices at once
            input_type = "radio"
        elif multiple:
            # Multiple choice: use checkboxes
            # Example: techniques (if user can select multiple techniques)
            input_type = "checkbox"
        else:
            # Larger list or default: use dropdown
            # Example: species (25 options) - dropdown with search is more usable
            input_type = "list"

        # QUIRK: Support two return formats for backward compatibility
        # - Flat format: Used in demo.qmd for direct inspection
        # - Nested format: Used in generator for CEDAR field creation
        # This avoids breaking existing code while providing clean API
        if flat_format:
            return {
                "requiredValue": is_required,
                "literals": literals,
                "multipleChoice": multiple,
                "inputType": input_type
            }

        return {
            "inputType": input_type,
            "valueConstraints": {
                "requiredValue": is_required,
                "literals": literals,
                "multipleChoice": multiple
            }
        }

    def load_instances(self, term_type: str) -> List[Dict]:
        """Load all instances for a term type (e.g., 'species')"""
        term_path = self.terminologies_path / term_type

        if not term_path.exists():
            return []

        instances = []
        for jsonld_file in term_path.glob("*.jsonld"):
            with open(jsonld_file) as f:
                data = json.load(f)
                instances.append({
                    "id": data.get("@id"),
                    "name": data.get("name"),
                    "ontology_id": data.get("preferredOntologyIdentifier")
                })

        instances.sort(key=lambda x: x["name"] or "")
        return instances
