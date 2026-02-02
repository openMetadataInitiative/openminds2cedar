"""CEDAR API client - Interact with CEDAR Workbench API."""

import os
from datetime import datetime, timezone
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()

# Constants
BASE_URL = "https://resource.metadatacenter.org"
TIMEOUT = 30


class CEDARClient:
    """Client for CEDAR Workbench API."""

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.getenv("CEDAR_API_KEY")
        if not self.api_key:
            raise ValueError("CEDAR_API_KEY not set")

        self.base_url = BASE_URL
        self.timeout = TIMEOUT
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

    def validate(self, element: dict) -> dict:
        """Validate element. Returns {"valid": bool, "errors": [...]}."""
        url = f"{self.base_url}/command/validate"
        params = {"resource_type": "element"}

        resp = requests.post(url, json=element, params=params, headers=self._headers(), timeout=self.timeout)

        if resp.status_code == 200:
            return {"valid": True, "errors": []}

        try:
            data = resp.json()
            return {"valid": False, "errors": data.get("errors", [resp.text])}
        except Exception:
            return {"valid": False, "errors": [resp.text]}

    def upload(self, element: dict, folder_id: str | None = None) -> dict:
        """Upload element. Returns {"success": bool, "id": str | None, "error": str | None}."""
        url = f"{self.base_url}/template-elements"

        upload_data = element.copy()
        timestamp = datetime.now(timezone.utc).isoformat()
        upload_data["pav:createdOn"] = timestamp
        upload_data["pav:lastUpdatedOn"] = timestamp

        params = {}
        target_folder = folder_id or self.folders.get("elements")
        if target_folder:
            params["folder_id"] = target_folder

        resp = requests.post(url, json=upload_data, params=params, headers=self._headers(), timeout=self.timeout)

        if resp.status_code in (200, 201):
            data = resp.json()
            return {"success": True, "id": data.get("@id"), "error": None}

        return {"success": False, "id": None, "error": resp.text}

    def upload_template(self, template: dict, folder_id: str | None = None) -> dict:
        """Upload template. Returns {"success": bool, "id": str | None, "error": str | None}."""
        url = f"{self.base_url}/templates"

        upload_data = template.copy()
        timestamp = datetime.now(timezone.utc).isoformat()
        upload_data["pav:createdOn"] = timestamp
        upload_data["pav:lastUpdatedOn"] = timestamp

        params = {}
        target_folder = folder_id or self.folders.get("templates")
        if target_folder:
            params["folder_id"] = target_folder

        resp = requests.post(url, json=upload_data, params=params, headers=self._headers(), timeout=self.timeout)

        if resp.status_code in (200, 201):
            data = resp.json()
            return {"success": True, "id": data.get("@id"), "error": None}

        return {"success": False, "id": None, "error": resp.text}

    def get_element(self, element_id: str) -> dict | None:
        """Fetch element by ID."""
        from urllib.parse import quote
        encoded_id = quote(element_id, safe='')
        url = f"{self.base_url}/template-elements/{encoded_id}"
        resp = requests.get(url, headers=self._headers(), timeout=self.timeout)
        if resp.status_code == 200:
            return resp.json()
        return None

    def validate_template(self, template: dict) -> dict:
        """Validate template. Returns {"valid": bool, "errors": [...]}."""
        url = f"{self.base_url}/command/validate"
        params = {"resource_type": "template"}

        resp = requests.post(url, json=template, params=params, headers=self._headers(), timeout=self.timeout)

        if resp.status_code == 200:
            return {"valid": True, "errors": []}

        try:
            data = resp.json()
            return {"valid": False, "errors": data.get("errors", [resp.text])}
        except Exception:
            return {"valid": False, "errors": [resp.text]}

    def list_folder(self, folder_id: str) -> list[dict]:
        """List contents of a folder."""
        from urllib.parse import quote
        encoded_id = quote(folder_id, safe='')
        url = f"{self.base_url}/folders/{encoded_id}/contents"
        resp = requests.get(url, headers=self._headers(), timeout=self.timeout)
        if resp.status_code == 200:
            data = resp.json()
            return data.get("resources", [])
        return []

    def get_template(self, template_id: str) -> dict | None:
        """Fetch template by ID."""
        from urllib.parse import quote
        encoded_id = quote(template_id, safe='')
        url = f"{self.base_url}/templates/{encoded_id}"
        resp = requests.get(url, headers=self._headers(), timeout=self.timeout)
        if resp.status_code == 200:
            return resp.json()
        return None

    def get_instance(self, instance_id: str) -> dict | None:
        """Fetch template instance by ID."""
        from urllib.parse import quote
        encoded_id = quote(instance_id, safe='')
        url = f"{self.base_url}/template-instances/{encoded_id}"
        resp = requests.get(url, headers=self._headers(), timeout=self.timeout)
        if resp.status_code == 200:
            return resp.json()
        return None

    def upload_instance(self, instance: dict, folder_id: str | None = None) -> dict:
        """Upload template instance. Returns {"success": bool, "id": str | None, "error": str | None}."""
        url = f"{self.base_url}/template-instances"

        upload_data = instance.copy()
        timestamp = datetime.now(timezone.utc).isoformat()
        upload_data["pav:createdOn"] = timestamp
        upload_data["pav:lastUpdatedOn"] = timestamp

        params = {}
        target_folder = folder_id or self.folders.get("instances")
        if target_folder:
            params["folder_id"] = target_folder

        resp = requests.post(url, json=upload_data, params=params, headers=self._headers(), timeout=self.timeout)

        if resp.status_code in (200, 201):
            data = resp.json()
            return {"success": True, "id": data.get("@id"), "error": None}

        return {"success": False, "id": None, "error": resp.text}

    def delete_element(self, element_id: str) -> dict:
        """Delete a template element."""
        from urllib.parse import quote
        encoded_id = quote(element_id, safe='')
        url = f"{self.base_url}/template-elements/{encoded_id}"
        resp = requests.delete(url, headers=self._headers(), timeout=self.timeout)
        if resp.status_code == 204:
            return {"success": True, "error": None}
        return {"success": False, "error": resp.text}

    def delete_template(self, template_id: str) -> dict:
        """Delete a template."""
        from urllib.parse import quote
        encoded_id = quote(template_id, safe='')
        url = f"{self.base_url}/templates/{encoded_id}"
        resp = requests.delete(url, headers=self._headers(), timeout=self.timeout)
        if resp.status_code == 204:
            return {"success": True, "error": None}
        return {"success": False, "error": resp.text}

    def delete_instance(self, instance_id: str) -> dict:
        """Delete a template instance."""
        from urllib.parse import quote
        encoded_id = quote(instance_id, safe='')
        url = f"{self.base_url}/template-instances/{encoded_id}"
        resp = requests.delete(url, headers=self._headers(), timeout=self.timeout)
        if resp.status_code == 204:
            return {"success": True, "error": None}
        return {"success": False, "error": resp.text}

    def clear_all(self, verbose: bool = True) -> dict:
        """Delete all instances, templates, and elements. WARNING: Destructive!"""
        deleted = {"instances": 0, "templates": 0, "elements": 0, "errors": []}

        if verbose:
            print("Deleting instances...")
        for item in self.list_folder(self.folders["instances"]):
            result = self.delete_instance(item["@id"])
            if result["success"]:
                deleted["instances"] += 1
                if verbose:
                    print(f"  Deleted: {item.get('schema:name', item['@id'])}")
            else:
                deleted["errors"].append(f"Instance {item['@id']}: {result['error']}")

        if verbose:
            print("Deleting templates...")
        for item in self.list_folder(self.folders["templates"]):
            result = self.delete_template(item["@id"])
            if result["success"]:
                deleted["templates"] += 1
                if verbose:
                    print(f"  Deleted: {item.get('schema:name', item['@id'])}")
            else:
                deleted["errors"].append(f"Template {item['@id']}: {result['error']}")

        if verbose:
            print("Deleting elements...")
        for item in self.list_folder(self.folders["elements"]):
            result = self.delete_element(item["@id"])
            if result["success"]:
                deleted["elements"] += 1
                if verbose:
                    print(f"  Deleted: {item.get('schema:name', item['@id'])}")
            else:
                deleted["errors"].append(f"Element {item['@id']}: {result['error']}")

        if verbose:
            print(f"Done: {deleted['instances']} instances, {deleted['templates']} templates, {deleted['elements']} elements")

        return deleted

    def sync_to_local(self, output_dir: str | Path, verbose: bool = True) -> dict:
        """Sync all CEDAR resources to local directory."""
        import json
        output_dir = Path(output_dir)

        synced = {"elements": 0, "templates": 0, "instances": 0, "errors": []}

        (output_dir / "elements").mkdir(parents=True, exist_ok=True)
        (output_dir / "templates").mkdir(parents=True, exist_ok=True)
        (output_dir / "instances").mkdir(parents=True, exist_ok=True)

        if verbose:
            print("Syncing elements...")
        for item in self.list_folder(self.folders["elements"]):
            element = self.get_element(item["@id"])
            if element:
                name = element.get("schema:name", "unnamed")
                with open(output_dir / "elements" / f"{name}.json", "w") as f:
                    json.dump(element, f, indent=2)
                synced["elements"] += 1
                if verbose:
                    print(f"  {name}.json")
            else:
                synced["errors"].append(f"Failed: {item['@id']}")

        if verbose:
            print("Syncing templates...")
        for item in self.list_folder(self.folders["templates"]):
            template = self.get_template(item["@id"])
            if template:
                name = template.get("schema:name", "unnamed")
                with open(output_dir / "templates" / f"{name}.json", "w") as f:
                    json.dump(template, f, indent=2)
                synced["templates"] += 1
                if verbose:
                    print(f"  {name}.json")
            else:
                synced["errors"].append(f"Failed: {item['@id']}")

        if verbose:
            print("Syncing instances...")
        for item in self.list_folder(self.folders["instances"]):
            instance = self.get_instance(item["@id"])
            if instance:
                name = instance.get("schema:name", "unnamed")
                with open(output_dir / "instances" / f"{name}.json", "w") as f:
                    json.dump(instance, f, indent=2)
                synced["instances"] += 1
                if verbose:
                    print(f"  {name}.json")
            else:
                synced["errors"].append(f"Failed: {item['@id']}")

        if verbose:
            print(f"Done: {synced['elements']} elements, {synced['templates']} templates, {synced['instances']} instances")

        return synced
