# Tests

Unit tests for openminds2cedar using pytest.

## Running

```bash
uv run pytest tests/ -v
```

## Structure

```
tests/
├── conftest.py              # Pytest fixtures
├── fixtures/                # Shared test data
│   └── __init__.py          # MOCK_SUBJECT_DATA, sample_cedar_instance(), etc.
├── test_elements.py         # Element generation
├── test_templates.py        # Template generation
├── test_cedar_to_openminds.py   # Basic conversion tests
└── test_generic_converter.py    # Generic type conversion tests
```

## Shared Fixtures

Test data in `tests/fixtures/__init__.py` (single source of truth):

| Fixture | Description |
|---------|-------------|
| `MOCK_SUBJECT_DATA` | Subject field values |
| `MOCK_SUBJECTSTATE_DATA` | SubjectState field values |
| `sample_cedar_instance()` | Complete Subject+SubjectState instance |
| `person_instance()` | Person instance |
| `tissue_sample_instance()` | TissueSample+TissueSampleState instance |

## Manual Testing

```bash
uv run python scripts/publish_test_resources.py
```

Clears CEDAR, uploads elements/templates/instances, converts, and validates.
