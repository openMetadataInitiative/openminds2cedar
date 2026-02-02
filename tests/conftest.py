"""Pytest fixtures for openminds2cedar tests."""

import pytest
from pathlib import Path


@pytest.fixture
def registry_dir():
    """Path to registry directory."""
    return Path(__file__).parent.parent / "src" / "openminds2cedar" / "registry"


@pytest.fixture
def output_dir(tmp_path):
    """Temporary output directory for generated files."""
    return tmp_path / "output"
