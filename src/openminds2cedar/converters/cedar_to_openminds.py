"""Convert CEDAR instances to openMINDS collections."""

import json
from pathlib import Path

from openminds import Collection

from .resolver import Resolver, TYPE_REGISTRY


class CEDARToOpenMINDSConverter:
    """Convert CEDAR instances to openMINDS Collection.

    Uses @context mapping to determine openMINDS types and converts
    any element generically based on its schema properties.
    """

    def __init__(self, resolver: Resolver | None = None):
        self.resolver = resolver or Resolver()

    def convert(self, instance_path: str | Path) -> Collection:
        """Convert a CEDAR instance JSON file to openMINDS Collection."""
        with open(instance_path) as f:
            return self.convert_instance(json.load(f))

    def convert_instance(self, instance: dict) -> Collection:
        """Convert a CEDAR instance dict to openMINDS Collection.

        Reads @context to map element names to openMINDS type URIs,
        then converts each element using the appropriate openMINDS class.
        """
        collection = Collection()
        context = instance.get("@context", {})

        # First pass: convert all elements and track by element name
        converted_objects: dict[str, list] = {}

        for element_name, type_uri in context.items():
            if not isinstance(type_uri, str) or not type_uri.startswith("https://openminds"):
                continue

            om_class = self.resolver.get_class_by_type_uri(type_uri)
            if not om_class:
                continue

            element_data = instance.get(element_name)
            if not element_data:
                continue

            # Handle both single objects and arrays
            data_list = element_data if isinstance(element_data, list) else [element_data]
            converted_objects[element_name] = []

            for data in data_list:
                obj = self._convert_element(data, om_class, converted_objects)
                converted_objects[element_name].append(obj)
                collection.add(obj)

        # Second pass: link objects that reference each other
        self._link_objects(converted_objects)

        return collection

    def _convert_element(self, data: dict, om_class: type, converted_objects: dict) -> object:
        """Convert a single CEDAR element to an openMINDS object."""
        kwargs = {}

        for prop in om_class.properties:
            value = self._extract_property_value(data, prop, converted_objects)
            if value is not None:
                kwargs[prop.name] = value

        return om_class(**kwargs)

    def _extract_property_value(self, data: dict, prop, converted_objects: dict):
        """Extract property value from CEDAR element data."""
        raw_value = self._get_value(data, prop.name)
        if raw_value is None:
            return None

        if not prop.is_link:
            # Simple literal value (string, etc.)
            return raw_value

        # Linked value - check if it's a controlled term
        for allowed_type in prop.types:
            if hasattr(allowed_type, "by_name"):
                # It's a controlled term - resolve by name
                try:
                    result = allowed_type.by_name(raw_value)
                    if result:
                        return result
                except (TypeError, AttributeError):
                    # by_name() can fail if term not found
                    continue

        # Not a controlled term - might need linking later
        return None

    def _link_objects(self, converted_objects: dict[str, list]):
        """Link objects based on property type compatibility.

        Introspects each object's properties and links to matching converted objects.
        Skips controlled terms (identified by having 'by_name' method).
        """
        # Map class -> objects (skip controlled terms)
        linkable: dict[type, list] = {}
        for objects in converted_objects.values():
            if objects:
                cls = type(objects[0])
                if not hasattr(cls, "by_name"):  # Not a controlled term
                    linkable[cls] = objects

        # For each non-controlled-term object, check link properties
        for objects in converted_objects.values():
            for obj in objects:
                cls = type(obj)
                if hasattr(cls, "by_name"):
                    continue

                for prop in cls.properties:
                    if not prop.is_link:
                        continue
                    # Check if any allowed type matches a linkable object
                    for allowed_type in prop.types:
                        if allowed_type in linkable:
                            targets = linkable[allowed_type]
                            setattr(obj, prop.name, targets if prop.multiple else targets[0])
                            break

    def _get_value(self, data: dict, field: str) -> str | None:
        """Extract value from CEDAR field structure.

        CEDAR fields have structure: {"@value": "actual value"}
        """
        if field_data := data.get(field):
            if isinstance(field_data, dict):
                value = field_data.get("@value")
                if value is not None and value != "null":
                    return value
        return None
