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

RESOURCE_TYPES = {
    "element": ("template-elements", "elements"),
    "template": ("templates", "templates"),
    "instance": ("template-instances", "instances"),
}


class CEDARError(Exception):
    """CEDAR API error."""

    pass


class CEDARClient:
    """Client for CEDAR Workbench API."""

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.getenv("CEDAR_API_KEY")
        if not self.api_key:
            raise CEDARError("CEDAR_API_KEY not set")

        self.folders = {
            "elements": os.getenv("CEDAR_FOLDER_ELEMENTS"),
            "templates": os.getenv("CEDAR_FOLDER_TEMPLATES"),
            "instances": os.getenv("CEDAR_FOLDER_INSTANCES"),
        }

    def _headers(self) -> dict:
        return {
            "Authorization": f"apiKey {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def _request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        url = f"{BASE_URL}/{endpoint}"
        return requests.request(method, url, headers=self._headers(), timeout=TIMEOUT, **kwargs)

    # --- Validate ---

    def validate(self, data: dict, resource_type: str = "element") -> dict:
        """Validate element or template. Returns {"valid": bool, "errors": [], "warnings": []}."""
        resp = self._request("POST", "command/validate", json=data, params={"resource_type": resource_type})
        if resp.status_code != 200:
            raise CEDARError(f"Validation request failed: {resp.text}")
        result = resp.json()
        return {
            "valid": str(result.get("validates", "")).lower() == "true",
            "errors": result.get("errors", []),
            "warnings": result.get("warnings", []),
        }

    def validate_template(self, template: dict) -> dict:
        return self.validate(template, "template")

    # --- CRUD ---

    def get(self, resource_id: str, resource_type: str = "element") -> dict:
        """Fetch resource by ID. Raises CEDARError if not found."""
        endpoint, _ = RESOURCE_TYPES[resource_type]
        resp = self._request("GET", f"{endpoint}/{quote(resource_id, safe='')}")
        if resp.status_code != 200:
            raise CEDARError(f"Failed to get {resource_type} {resource_id}: {resp.text}")
        return resp.json()

    def get_element(self, element_id: str) -> dict:
        return self.get(element_id, "element")

    def get_template(self, template_id: str) -> dict:
        return self.get(template_id, "template")

    def get_instance(self, instance_id: str) -> dict:
        return self.get(instance_id, "instance")

    def upload(self, data: dict, resource_type: str = "element", folder_id: str | None = None) -> dict:
        """Upload resource. Returns {"success": bool, "id": str, "error": str}."""
        endpoint, folder_key = RESOURCE_TYPES[resource_type]

        upload_data = data.copy()
        if upload_data.get("@id", "").startswith("urn:"):
            upload_data["@id"] = None
        timestamp = datetime.now(timezone.utc).isoformat()
        upload_data["pav:createdOn"] = timestamp
        upload_data["pav:lastUpdatedOn"] = timestamp

        params = {"folder_id": folder_id or self.folders.get(folder_key)} if (folder_id or self.folders.get(folder_key)) else {}

        resp = self._request("POST", endpoint, json=upload_data, params=params)
        if resp.status_code in (200, 201):
            return {"success": True, "id": resp.json().get("@id"), "error": None}
        return {"success": False, "id": None, "error": resp.text}

    def upload_template(self, template: dict, folder_id: str | None = None) -> dict:
        return self.upload(template, "template", folder_id)

    def upload_instance(self, instance: dict, folder_id: str | None = None) -> dict:
        return self.upload(instance, "instance", folder_id)

    def delete(self, resource_id: str, resource_type: str = "element") -> dict:
        """Delete resource. Returns {"success": bool, "error": str}."""
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
        """List folder contents. Raises CEDARError on failure."""
        resp = self._request("GET", f"folders/{quote(folder_id, safe='')}/contents")
        if resp.status_code != 200:
            raise CEDARError(f"Failed to list folder {folder_id}: {resp.text}")
        return resp.json().get("resources", [])

    def create_folder(self, name: str, parent_folder_id: str, description: str = "") -> dict:
        """Create subfolder. Returns {"success": bool, "id": str, "error": str}."""
        data = {"folderId": parent_folder_id, "name": name, "description": description or f"{name} folder"}
        resp = self._request("POST", "folders", json=data)
        if resp.status_code in (200, 201):
            return {"success": True, "id": resp.json().get("@id"), "error": None}
        return {"success": False, "id": None, "error": resp.text}

    def get_or_create_subfolder(self, name: str, parent_folder_id: str) -> str:
        """Get or create subfolder. Raises CEDARError on failure."""
        for item in self.list_folder(parent_folder_id):
            if item.get("schema:name") == name:
                return item["@id"]
        result = self.create_folder(name, parent_folder_id)
        if not result["success"]:
            raise CEDARError(f"Failed to create folder {name}: {result['error']}")
        return result["id"]

    # --- Bulk operations ---

    def clear_all(self, verbose: bool = True) -> dict:
        """Delete all instances, templates, and elements (in order). WARNING: Destructive!"""
        deleted = {"instances": 0, "templates": 0, "elements": 0, "errors": []}

        for rtype in ["instance", "template", "element"]:
            _, folder_key = RESOURCE_TYPES[rtype]
            if verbose:
                print(f"Deleting {folder_key}...")

            for item in self.list_folder(self.folders[folder_key]):
                # Handle subfolders (for elements)
                if item.get("resourceType") == "folder":
                    for sub_item in self.list_folder(item["@id"]):
                        result = self.delete(sub_item["@id"], rtype)
                        if result["success"]:
                            deleted[folder_key] += 1
                            if verbose:
                                print(f"  Deleted: {sub_item.get('schema:name')}")
                        else:
                            deleted["errors"].append(f"{rtype} {sub_item['@id']}: {result['error']}")
                else:
                    result = self.delete(item["@id"], rtype)
                    if result["success"]:
                        deleted[folder_key] += 1
                        if verbose:
                            print(f"  Deleted: {item.get('schema:name')}")
                    else:
                        deleted["errors"].append(f"{rtype} {item['@id']}: {result['error']}")

        if verbose:
            print(f"Done: {deleted['instances']} instances, {deleted['templates']} templates, {deleted['elements']} elements")
        return deleted

    def download_all(self, output_dir: str | Path, verbose: bool = True) -> dict:
        """Download all resources to local directory. Elements organized by module subfolder."""
        output_dir = Path(output_dir)
        downloaded = {"elements": 0, "templates": 0, "instances": 0}

        # Download elements
        if verbose:
            print("Downloading elements...")
        for item in self.list_folder(self.folders["elements"]):
            if item.get("resourceType") == "folder":
                module = item.get("schema:name")
                module_dir = output_dir / "elements" / module
                module_dir.mkdir(parents=True, exist_ok=True)
                for elem_item in self.list_folder(item["@id"]):
                    element = self.get_element(elem_item["@id"])
                    name = element.get("schema:name")
                    (module_dir / f"{name}.json").write_text(json.dumps(element, indent=2))
                    downloaded["elements"] += 1
                    if verbose:
                        print(f"  {module}/{name}.json")
            else:
                # Element directly in root folder
                element = self.get_element(item["@id"])
                name = element.get("schema:name")
                elem_dir = output_dir / "elements"
                elem_dir.mkdir(parents=True, exist_ok=True)
                (elem_dir / f"{name}.json").write_text(json.dumps(element, indent=2))
                downloaded["elements"] += 1
                if verbose:
                    print(f"  {name}.json")

        # Download templates and instances
        for rtype in ["template", "instance"]:
            _, folder_key = RESOURCE_TYPES[rtype]
            rtype_dir = output_dir / folder_key
            rtype_dir.mkdir(parents=True, exist_ok=True)

            if verbose:
                print(f"Downloading {folder_key}...")

            for item in self.list_folder(self.folders[folder_key]):
                resource = self.get(item["@id"], rtype)
                name = resource.get("schema:name")
                (rtype_dir / f"{name}.json").write_text(json.dumps(resource, indent=2))
                downloaded[folder_key] += 1
                if verbose:
                    print(f"  {name}.json")

        if verbose:
            print(f"Done: {downloaded['elements']} elements, {downloaded['templates']} templates, {downloaded['instances']} instances")
        return downloaded
