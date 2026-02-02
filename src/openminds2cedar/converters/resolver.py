"""Resolver - Runtime lookup using openminds Python package."""

import openminds.latest as om


def _build_type_registry() -> dict[str, type]:
    """Build mapping of type URIs to openMINDS classes.

    Scans all openMINDS modules and maps type_ URIs to their classes.
    E.g., "https://openminds.om-i.org/types/Subject" -> om.core.Subject
    """
    registry = {}
    modules = ["core", "controlled_terms", "sands", "ephys", "computation", "publications"]

    for module_name in modules:
        module = getattr(om, module_name, None)
        if not module:
            continue
        for class_name in dir(module):
            if class_name.startswith("_"):
                continue
            cls = getattr(module, class_name)
            if hasattr(cls, "type_") and isinstance(cls.type_, str):
                registry[cls.type_] = cls

    return registry


# Build registry once at import time
TYPE_REGISTRY = _build_type_registry()


class Resolver:
    """Resolve openMINDS classes and controlled terms."""

    def __init__(self):
        self._cache: dict = {}

    def resolve_class(self, path: str):
        """Resolve 'controlled_terms.Species' -> om.controlled_terms.Species."""
        if path in self._cache:
            return self._cache[path]

        obj = om
        for part in path.split("."):
            obj = getattr(obj, part, None)
            if obj is None:
                raise AttributeError(f"Cannot resolve '{path}'")

        self._cache[path] = obj
        return obj

    def lookup(self, term_class_path: str, value: str) -> dict | None:
        """Lookup controlled term by name. Returns {id, name} or None."""
        term_class = self.resolve_class(term_class_path)
        result = term_class.by_name(value)
        if result:
            return {"id": result.id, "name": result.name}
        return None

    def get_options(self, term_class_path: str) -> list[dict]:
        """Get all options. Returns [{label, id}, ...] sorted by label."""
        term_class = self.resolve_class(term_class_path)
        return sorted(
            [{"label": i.name, "id": i.id} for i in term_class.instances()],
            key=lambda x: x["label"],
        )

    def get_class_by_type_uri(self, type_uri: str) -> type | None:
        """Get openMINDS class by its type URI.

        E.g., "https://openminds.om-i.org/types/Subject" -> om.core.Subject
        """
        return TYPE_REGISTRY.get(type_uri)

    def get_property_info(self, om_class: type) -> dict[str, dict]:
        """Get property information for an openMINDS class.

        Returns dict mapping snake_case property names to their metadata:
        {
            "species": {"path": "species", "required": True, ...},
            "biological_sex": {"path": "biologicalSex", "required": False, ...},
        }
        """
        if not hasattr(om_class, "properties"):
            return {}

        props = {}
        for prop in om_class.properties:
            props[prop.name] = {
                "path": prop.path,  # camelCase JSON-LD path
                "required": getattr(prop, "required", False),
            }
        return props
