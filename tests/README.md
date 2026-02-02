# Tests

Unit tests for openminds2cedar using pytest fixtures.

## Running

```bash
uv run pytest tests/ -v
```

## Structure

```
tests/
├── conftest.py                  # Shared fixtures
├── test_generators.py           # Element/template generation
└── test_cedar_to_openminds.py   # CEDAR -> openMINDS conversion
```

## Fixtures

| Fixture | Description |
|---------|-------------|
| `element_generator` | CEDARElementGenerator instance |
| `template_generator` | CEDARTemplateGenerator instance |
| `converter` | CEDARToOpenMINDSConverter instance |
| `sample_cedar_instance` | Complete CEDAR instance for testing |
| `instance_with_nulls` | Instance with null values for edge cases |
