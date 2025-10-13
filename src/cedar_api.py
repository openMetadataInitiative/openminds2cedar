#!/usr/bin/env python3
"""
CEDAR Workbench API Client

Simple client for uploading CEDAR elements to CEDAR Workbench.
Requires CEDAR_API_KEY environment variable.

API Documentation: https://metadatacenter.readthedocs.io/
Element Upload Endpoint: https://resource.metadatacenter.org/elements
"""

import os
import json
import yaml
import requests
from typing import Dict, Optional
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class CEDARAPIError(Exception):
    """Custom exception for CEDAR API errors"""
    pass


class CEDARAPIClient:
    """
    Client for CEDAR Workbench API

    Supports uploading template elements to CEDAR Workbench.
    Uses apiKey authentication as specified in CEDAR documentation.
    """

    def __init__(self, config_path: str = "config.yaml", api_key: Optional[str] = None):
        """
        Initialize CEDAR API client

        Args:
            config_path: Path to configuration file
            api_key: CEDAR API key (if None, reads from CEDAR_API_KEY env var)

        Raises:
            ValueError: If API key is not provided
        """
        self.config = self._load_config(config_path)
        self.api_key = api_key or os.getenv("CEDAR_API_KEY")

        if not self.api_key:
            raise ValueError(
                "CEDAR API key required. Set CEDAR_API_KEY environment variable "
                "or pass api_key parameter."
            )

        # CEDAR API endpoints as per documentation
        self.base_url = self.config["cedar"]["api"]["base_url"]
        self.timeout = self.config["cedar"]["api"]["timeout"]
        self.folder_id = self.config["cedar"]["api"].get("folder_id")

        # Setup session with CEDAR-required headers
        # Authorization format: "apiKey <KEY>" as per CEDAR docs
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"apiKey {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        })

    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML file"""
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)

    def upload_element(self, element: Dict, folder_id: Optional[str] = None) -> Dict:
        """
        Upload a CEDAR element to the workspace

        Uses POST to https://resource.metadatacenter.org/elements
        as specified in CEDAR API documentation.

        Args:
            element: CEDAR element dictionary (must be valid TemplateElement)
            folder_id: Target folder ID (uses config default if None)

        Returns:
            Response from CEDAR API with created element details including @id

        Raises:
            CEDARAPIError: If upload fails
        """
        # Prepare element for upload
        upload_data = element.copy()

        # Add timestamps (CEDAR metadata fields)
        timestamp = datetime.utcnow().isoformat() + "Z"
        upload_data["pav:createdOn"] = timestamp
        upload_data["pav:lastUpdatedOn"] = timestamp

        # Build URL - CEDAR element endpoint
        url = f"{self.base_url}/template-elements"

        # Add folder parameter if specified
        # Note: Parameter name is "folder_id" with underscore, not "folderId"
        # requests library will automatically URL encode the parameter
        params = {}
        target_folder = folder_id or self.folder_id
        if target_folder:
            params["folder_id"] = target_folder
            print(f"Uploading to folder: {target_folder}")
        else:
            print("No folder specified - uploading to workspace root")

        try:
            # POST request as per CEDAR API docs
            response = self.session.post(
                url,
                json=upload_data,
                params=params,
                timeout=self.timeout
            )

            # Check for HTTP errors
            response.raise_for_status()

            result = response.json()
            element_name = element.get("schema:name", "unknown")
            cedar_id = result.get("@id", "unknown")

            print(f"Uploaded: {element_name} -> {cedar_id}")

            return result

        except requests.exceptions.HTTPError as e:
            # Parse error response
            try:
                error_detail = e.response.json()
                error_msg = f"HTTP {e.response.status_code}: {error_detail}"
            except:
                error_msg = f"HTTP {e.response.status_code}: {e.response.text}"

            raise CEDARAPIError(error_msg) from e

        except requests.exceptions.RequestException as e:
            raise CEDARAPIError(f"Request failed: {e}") from e

    def upload_element_from_file(self, file_path: str, folder_id: Optional[str] = None) -> Dict:
        """
        Upload a CEDAR element from a JSON file

        Args:
            file_path: Path to element JSON file
            folder_id: Target folder ID (uses config default if None)

        Returns:
            Response from CEDAR API

        Raises:
            CEDARAPIError: If upload fails
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            element = json.load(f)

        return self.upload_element(element, folder_id)

    def validate_element(self, element: Dict) -> Dict:
        """
        Validate a CEDAR element without uploading

        Uses CEDAR validation endpoint as per documentation.

        Args:
            element: CEDAR element dictionary

        Returns:
            Validation response

        Raises:
            CEDARAPIError: If validation fails
        """
        url = f"{self.base_url}/command/validate"
        params = {"resource_type": "element"}

        try:
            response = self.session.post(
                url,
                json=element,
                params=params,
                timeout=self.timeout
            )

            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            raise CEDARAPIError(f"Validation failed: {e}") from e
