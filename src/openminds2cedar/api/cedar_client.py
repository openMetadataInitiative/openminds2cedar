"""CEDAR API client."""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote

import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://resource.metadatacenter.org"
TIMEOUT = 30

# Resource type -> (endpoint, folder key)
RESOURCE_TYPES = {
    "element": ("template-elements", "elements"),
    "template": ("templates", "templates"),
    "instance": ("template-instances", "instances"),
}


class CEDARClient:
    """Client for CEDAR Workbench API."""

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.getenv("CEDAR_API_KEY")
        if not self.api_key:
            raise ValueError("CEDAR_API_KEY not set")

        self.folders = {
            "elements": os.getenv("CEDAR_FOLDER_ELEMENTS"),
            "templates": os.getenv("CEDAR_FOLDER_TEMPLATES"),
            "instances": os.getenv("CEDAR_FOLDER_INSTANCES"),
            "test": os.getenv("CEDAR_FOLDER_TEST"),
        }

    def _headers(self) -> dict:
        return {
            "Authorization": f"apiKey {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def _request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Make API request."""
        url = f"{BASE_URL}/{endpoint}"
        return requests.request(method, url, headers=self._headers(), timeout=TIMEOUT, **kwargs)

    # --- Validate ---

    def validate(self, data: dict, resource_type: str = "element") -> dict:
        """Validate element or template. Returns {"valid": bool, "errors": [], "warnings": []}."""
        resp = self._request("POST", "command/validate", json=data, params={"resource_type": resource_type})
        if resp.status_code == 200:
            result = resp.json()
            return {
                "valid": str(result.get("validates", "")).lower() == "true",
                "errors": result.get("errors", []),
                "warnings": result.get("warnings", []),
            }
        return {"valid": False, "errors": [resp.text], "warnings": []}

    def validate_template(self, template: dict) -> dict:
        return self.validate(template, "template")

    # --- CRUD ---

    def get(self, resource_id: str, resource_type: str = "element") -> dict | None:
        """Fetch resource by ID."""
        endpoint, _ = RESOURCE_TYPES[resource_type]
        resp = self._request("GET", f"{endpoint}/{quote(resource_id, safe='')}")
        return resp.json() if resp.status_code == 200 else None

    def get_element(self, element_id: str) -> dict | None:
        return self.get(element_id, "element")

    def get_template(self, template_id: str) -> dict | None:
        return self.get(template_id, "template")

    def get_instance(self, instance_id: str) -> dict | None:
        return self.get(instance_id, "instance")

    def upload(self, data: dict, resource_type: str = "element", folder_id: str | None = None) -> dict:
        """Upload resource. Returns {"success": bool, "id": str | None, "error": str | None}."""
        endpoint, folder_key = RESOURCE_TYPES[resource_type]

        upload_data = data.copy()
        # Clear local URN IDs - CEDAR assigns real IDs on upload
        if upload_data.get("@id", "").startswith("urn:"):
            upload_data["@id"] = None
        timestamp = datetime.now(timezone.utc).isoformat()
        upload_data["pav:createdOn"] = timestamp
        upload_data["pav:lastUpdatedOn"] = timestamp

        params = {}
        if target := (folder_id or self.folders.get(folder_key)):
            params["folder_id"] = target

        resp = self._request("POST", endpoint, json=upload_data, params=params)
        if resp.status_code in (200, 201):
            return {"success": True, "id": resp.json().get("@id"), "error": None}
        return {"success": False, "id": None, "error": resp.text}

    def upload_template(self, template: dict, folder_id: str | None = None) -> dict:
        return self.upload(template, "template", folder_id)

    def upload_instance(self, instance: dict, folder_id: str | None = None) -> dict:
        return self.upload(instance, "instance", folder_id)

    def delete(self, resource_id: str, resource_type: str = "element") -> dict:
        """Delete resource. Returns {"success": bool, "error": str | None}."""
        endpoint, _ = RESOURCE_TYPES[resource_type]
        resp = self._request("DELETE", f"{endpoint}/{quote(resource_id, safe='')}")
        if resp.status_code == 204:
            return {"success": True, "error": None}
        return {"success": False, "error": resp.text}

    def delete_element(self, element_id: str) -> dict:
        return self.delete(element_id, "element")

    def delete_template(self, template_id: str) -> dict:
        return self.delete(template_id, "template")

    def delete_instance(self, instance_id: str) -> dict:
        return self.delete(instance_id, "instance")

    # --- Folder operations ---

    def list_folder(self, folder_id: str) -> list[dict]:
        """List contents of a folder."""
        resp = self._request("GET", f"folders/{quote(folder_id, safe='')}/contents")
        return resp.json().get("resources", []) if resp.status_code == 200 else []

    def clear_all(self, verbose: bool = True) -> dict:
        """Delete all instances, templates, and elements. WARNING: Destructive!"""
        deleted = {"instances": 0, "templates": 0, "elements": 0, "errors": []}

        for rtype in ["instance", "template", "element"]:
            _, folder_key = RESOURCE_TYPES[rtype]
            if verbose:
                print(f"Deleting {folder_key}...")

            for item in self.list_folder(self.folders[folder_key]):
                result = self.delete(item["@id"], rtype)
                if result["success"]:
                    deleted[folder_key] += 1
                    if verbose:
                        print(f"  Deleted: {item.get('schema:name', item['@id'])}")
                else:
                    deleted["errors"].append(f"{rtype} {item['@id']}: {result['error']}")

        if verbose:
            print(f"Done: {deleted['instances']} instances, {deleted['templates']} templates, {deleted['elements']} elements")
        return deleted

    def sync_to_local(self, output_dir: str | Path, verbose: bool = True) -> dict:
        """Sync all CEDAR resources to local directory."""
        output_dir = Path(output_dir)
        synced = {"elements": 0, "templates": 0, "instances": 0, "errors": []}

        for rtype in ["element", "template", "instance"]:
            _, folder_key = RESOURCE_TYPES[rtype]
            (output_dir / folder_key).mkdir(parents=True, exist_ok=True)

            if verbose:
                print(f"Syncing {folder_key}...")

            for item in self.list_folder(self.folders[folder_key]):
                resource = self.get(item["@id"], rtype)
                if resource:
                    name = resource.get("schema:name", "unnamed")
                    (output_dir / folder_key / f"{name}.json").write_text(json.dumps(resource, indent=2))
                    synced[folder_key] += 1
                    if verbose:
                        print(f"  {name}.json")
                else:
                    synced["errors"].append(f"Failed: {item['@id']}")

        if verbose:
            print(f"Done: {synced['elements']} elements, {synced['templates']} templates, {synced['instances']} instances")
        return synced
