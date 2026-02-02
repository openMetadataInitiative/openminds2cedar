"""Resolver - Runtime lookup using openminds Python package."""

import openminds.latest as om


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
