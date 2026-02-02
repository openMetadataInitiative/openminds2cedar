# API Module

CEDAR Workbench API client with explicit error handling.

## CEDARClient

```python
from openminds2cedar.api import CEDARClient, CEDARError

client = CEDARClient()  # Uses CEDAR_* env vars from .env

# Validate
client.validate(element)           # Raises CEDARError on failure
client.validate_template(template)

# Upload (returns {"success": bool, "id": str, "error": str})
client.upload(element)
client.upload_template(template)
client.upload_instance(instance)

# Fetch (raises CEDARError if not found)
client.get_element(id)
client.get_template(id)
client.get_instance(id)

# Folders
client.list_folder(folder_id)
client.create_folder(name, parent_id)
client.get_or_create_subfolder(name, parent_id)

# Delete (returns {"success": bool, "error": str})
client.delete_element(id)
client.delete_template(id)
client.delete_instance(id)

# Bulk operations
client.download_all("output/")  # Download all (elements organized by module)
client.clear_all()              # Delete all (WARNING: destructive)
```
