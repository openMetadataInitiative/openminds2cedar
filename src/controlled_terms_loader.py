#!/usr/bin/env python3
"""
Controlled Terms Loader - Load openMINDS instances for CEDAR value lists
"""

import json
from pathlib import Path
from typing import List, Dict


class ControlledTermsLoader:
    """Load controlled term instances from openMINDS_instances"""

    def __init__(self, instances_path: str = "external/openMINDS_instances/instances/latest/terminologies"):
        self.terminologies_path = Path(instances_path)

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

    def create_cedar_literals(self, instances: List[Dict]) -> List[Dict]:
        """Convert instances to CEDAR literals format"""
        return [{"label": inst["name"]} for inst in instances if inst.get("name")]
