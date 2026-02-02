# User Guide

## User Journeys

### Developer: Create Elements & Templates

```
Generate -> Validate -> Publish
```

1. **Generate** elements from openMINDS schemas (offline)
2. **Create** templates combining elements (offline)
3. **Validate** via CEDAR API (online)
4. **Publish** to CEDAR when ready (online)

### Curator: Convert Instances to openMINDS

```
Instance ID -> Convert -> openMINDS JSON-LD
```

1. Researcher fills template on CEDAR Workbench
2. Curator runs `convert` with instance ID
3. Output: validated openMINDS collection

---

## Testing

### Unit Tests (Offline)

Test core logic without CEDAR API:

```bash
uv run pytest tests/ -v --ignore=tests/integration/
```

Uses local fixtures with stable URN IDs:
- `tests/fixtures/elements/` - Generated elements
- `tests/fixtures/templates/` - Generated templates
- `tests/fixtures/instances/` - Mock filled instances

### Integration Tests (Online)

Test CEDAR API interaction:

```bash
uv run pytest tests/integration/ -v
```

Requires `CEDAR_API_KEY` environment variable.

---

## ID Strategy

| Phase | ID Format | Example |
|-------|-----------|---------|
| Development | Local URN | `urn:openminds2cedar:element:core.Subject` |
| Production | CEDAR URL | `https://repo.metadatacenter.org/template-elements/...` |

Local URNs are deterministic and stable for testing.
CEDAR assigns real URLs on publish.

---

## Quick Reference

```bash
# Developer workflow
openminds2cedar generate core.Subject      # Generate element
openminds2cedar template my-template ...   # Create template
openminds2cedar validate output/           # Validate via API
openminds2cedar publish output/            # Publish to CEDAR

# Curator workflow
openminds2cedar convert <instance-id>      # Convert to openMINDS
openminds2cedar convert path/to/file.json  # Or from local file
```
