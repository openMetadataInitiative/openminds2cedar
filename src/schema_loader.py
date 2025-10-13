#!/usr/bin/env python3
"""
Schema Loader - Load openMINDS schemas from git submodule
"""

import json
import yaml
from pathlib import Path
from typing import Dict


class OpenMINDSSchemaLoader:
    """Load openMINDS schemas from local git submodule"""

    def __init__(self, config_path: str = "config.yaml"):
        """Initialize schema loader with config file"""
        self.config = self._load_config(config_path)
        self.submodule_path = Path(self.config["openminds"]["submodule_path"])
        self.version = self.config["openminds"]["version"]
        self.schemas_config = self.config["openminds"]["schemas"]
        self.base_path = self.submodule_path / "schemas" / self.version

        if not self.submodule_path.exists():
            raise FileNotFoundError(
                f"openMINDS submodule not found at {self.submodule_path}. "
                "Run: git submodule update --init --recursive"
            )

    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML file"""
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)

    def load_schema(self, category: str, subcategory: str, filename: str) -> Dict:
        """Load a single schema file"""
        schema_path = self.base_path / category / subcategory / filename

        if not schema_path.exists():
            raise FileNotFoundError(f"Schema not found: {schema_path}")

        with open(schema_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def load_all_configured_schemas(self) -> Dict[str, Dict]:
        """
        Load all schemas defined in configuration

        Returns:
            Dict mapping schema_id to schema content (format: category/subcategory/filename)
        """
        all_schemas = {}

        for category, subcategories in self.schemas_config.items():
            if not subcategories:
                continue

            for subcategory, filenames in subcategories.items():
                if not filenames:
                    continue

                for filename in filenames:
                    try:
                        schema = self.load_schema(category, subcategory, filename)
                        schema_id = f"{category}/{subcategory}/{filename}"
                        all_schemas[schema_id] = schema
                        print(f"Loaded: {schema_id}")
                    except Exception as e:
                        print(f"Failed: {category}/{subcategory}/{filename} - {e}")

        print(f"\nLoaded {len(all_schemas)} schemas")
        return all_schemas
