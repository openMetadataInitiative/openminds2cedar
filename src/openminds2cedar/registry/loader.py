"""Registry - Load schema and field configurations from YAML."""

from pathlib import Path
import yaml


class Registry:
    """Load and access schema/field configurations."""

    def __init__(self, registry_dir: Path | None = None):
        self.dir = registry_dir or Path(__file__).parent
        self._schemas = yaml.safe_load((self.dir / "schemas.yaml").read_text())
        self._fields = yaml.safe_load((self.dir / "fields.yaml").read_text())

    @property
    def openminds_version(self) -> str:
        return self._schemas.get("openminds_version", "latest")

    @property
    def schemas(self) -> list[str]:
        """Schema paths like ['core.Subject', 'core.SubjectState', ...]."""
        result = []
        for module, classes in self._schemas.get("schemas", {}).items():
            result.extend(f"{module}.{c}" for c in classes)
        return result

    def field(self, name: str) -> dict:
        """Get field config. Raises KeyError if not found."""
        fields = self._fields.get("fields", {})
        if name not in fields:
            raise KeyError(f"Field '{name}' not in fields.yaml")
        return fields[name]

    def has_field(self, name: str) -> bool:
        """Check if field exists in registry."""
        return name in self._fields.get("fields", {})
