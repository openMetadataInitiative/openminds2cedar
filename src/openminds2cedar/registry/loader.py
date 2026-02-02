"""Registry - Load schema and field configurations from YAML."""

from pathlib import Path
import yaml


class Registry:
    """Load and access schema/field configurations."""

    def __init__(self, registry_dir: Path | None = None):
        self.dir = registry_dir or Path(__file__).parent
        self._schemas = yaml.safe_load((self.dir / "schemas.yaml").read_text())
        self._fields = yaml.safe_load((self.dir / "fields.yaml").read_text())
        self._templates = yaml.safe_load((self.dir / "templates.yaml").read_text())
        self._controlled_terms = self._fields.get("controlled_terms", {})

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

    def has_field(self, name: str) -> bool:
        """Check if field is a controlled term."""
        return name in self._controlled_terms

    def field(self, name: str) -> dict:
        """Get field config. Returns {"term_class": ...} for controlled terms."""
        if name in self._controlled_terms:
            return {"term_class": self._controlled_terms[name]}
        raise KeyError(f"Field '{name}' not in registry")

    @property
    def templates(self) -> list[str]:
        """Template names like ['subject-study', 'tissue-sample-study', ...]."""
        return list(self._templates.get("templates", {}).keys())

    def template(self, name: str) -> dict:
        """Get template definition with description and elements list."""
        templates = self._templates.get("templates", {})
        if name not in templates:
            raise KeyError(f"Template '{name}' not in registry")
        return templates[name]
