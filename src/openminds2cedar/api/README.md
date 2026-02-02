# API Module

CEDAR Workbench API client.

## CEDARClient

```python
from openminds2cedar.api import CEDARClient

client = CEDARClient()  # Uses CEDAR_* env vars from .env

# Upload/validate
client.validate(element)
client.upload(element)
client.upload_template(template)
client.upload_instance(instance)

# Fetch
client.get_element(id)
client.get_template(id)
client.get_instance(id)
client.list_folder(folder_id)

# Delete
client.delete_element(id)
client.delete_template(id)
client.delete_instance(id)

# Convenience
client.sync_to_local("data/cedar")  # Download all resources
client.clear_all()                   # Delete all (dev only)
```
