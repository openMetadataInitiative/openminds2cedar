# Next Steps: Semantic Robustness Roadmap

This document outlines the path from the current MVP implementation to a fully semantically robust solution.

## Current State (MVP)

### What Works
- User-friendly UI with dropdowns and radio buttons
- Automatic controlled term detection and integration
- Full CEDAR validation compliance
- Exact term control from openMINDS instances

### Limitations
- Semantic IRIs not preserved in field values
- No direct ontology integration
- Static term lists
- No custom vocabulary mappings

## Enhancement Roadmap

### Phase 1: Semantic IRI Preservation (Short-term)

**Goal**: Preserve openMINDS IRIs while maintaining user-friendly UI

#### Option A: Extended Field Description

Store openMINDS IRI mappings in field metadata:

```python
def _create_controlled_term_field(self, field_name, ...):
    instances = self.controlled_terms_loader.load_instances(field_name)

    # Build mapping table
    description = field_spec.get("description", "")
    description += "\n\nopenMINDS Term Mappings:\n"
    for inst in instances:
        description += f"- {inst['name']}: {inst['id']}\n"

    field["schema:description"] = description
```

**Pros**: Simple, no validation impact
**Cons**: Not machine-readable, manual lookup required

#### Option B: Custom Property

Add custom property to store mappings:

```python
field["openminds:termMappings"] = {
    inst["name"]: {
        "openminds_id": inst["id"],
        "ontology_id": inst.get("ontology_id")
    }
    for inst in instances
}
```

**Pros**: Machine-readable, structured data
**Cons**: Non-standard, may affect CEDAR validation

#### Option C: skos:altLabel

Use SKOS properties for alternate labels:

```python
field["properties"]["skos:altLabel"] = {
    "type": "array",
    "items": {"type": "string"}
}

field["skos:altLabel"] = [inst["id"] for inst in instances]
```

**Pros**: Semantic web standard, widely recognized
**Cons**: Complex structure, may need CEDAR schema adjustments

**Recommendation**: Start with Option A for immediate implementation, migrate to Option C for semantic web compliance.

### Phase 2: InterLex Integration (Medium-term)

**Goal**: Create persistent identifiers for openMINDS terms

#### Steps

1. **Register Terms in InterLex**
   - Create InterLex account at https://scicrunch.org/InterLex
   - Register controlled term types (biologicalSex, species, etc.)
   - Create ILX: identifiers for each instance
   - Link to both openMINDS IRIs and ontology terms

2. **Update Loader**
```python
class ControlledTermsLoader:
    def get_interlex_mappings(self, field_name):
        instances = self.load_instances(field_name)

        interlex_terms = []
        for inst in instances:
            interlex_terms.append({
                "label": inst["name"],
                "ilx_id": self._lookup_interlex_id(inst["id"]),
                "openminds_id": inst["id"],
                "ontology_id": inst.get("ontology_id")
            })

        return interlex_terms
```

3. **Use in CEDAR Fields**
```python
value_constraints = {
    "requiredValue": is_required,
    "literals": [
        {
            "label": term["label"],
            "uri": term["ilx_id"]  # InterLex IRI
        }
        for term in interlex_terms
    ]
}
```

**Benefits**:
- Persistent, resolvable identifiers
- Community reusability
- Links to multiple ontologies
- CEDAR-compatible

**Effort**: High (requires external registration)
**Timeline**: 2-4 weeks for initial setup

### Phase 3: BioPortal Value Sets (Medium-term)

**Goal**: Leverage existing ontology infrastructure

#### Steps

1. **Create BioPortal Value Sets**
   - Register at https://bioportal.bioontology.org
   - Create provisional classes for openMINDS terms
   - Map to ontology equivalents

2. **Reference in CEDAR**
```python
value_constraints = {
    "requiredValue": is_required,
    "valueSets": [{
        "vsCollection": f"openMINDS-{field_name}",
        "uri": f"https://bioportal.bioontology.org/valuesets/{collection_id}",
        "name": f"openMINDS {field_name} Terms",
        "numTerms": len(instances)
    }]
}
```

**Benefits**:
- Leverages BioPortal infrastructure
- CEDAR already integrates with BioPortal
- Ontology autocomplete features

**Challenges**:
- Value sets may not render as simple dropdowns
- Requires BioPortal account and maintenance
- Less direct control over term selection

**Timeline**: 3-6 weeks

### Phase 4: Hybrid Approach (Long-term)

**Goal**: Combine literal UI with semantic backend

#### Architecture

```python
def _create_controlled_term_field_hybrid(self, field_name, ...):
    instances = self.controlled_terms_loader.load_instances(field_name)

    # For UI: Simple literals
    literals = [{"label": inst["name"]} for inst in instances]

    # For semantics: Ontology classes with mappings
    classes = []
    for inst in instances:
        if inst.get("ontology_id"):
            classes.append({
                "source": "NCBITAXON" if "NCBITaxon" in inst["ontology_id"] else "PATO",
                "prefLabel": inst["name"],
                "uri": inst["ontology_id"],
                "label": inst["name"],
                "openminds:id": inst["id"]  # Custom property
            })

    return {
        "inputType": "list",  # User-friendly dropdown
        "valueConstraints": {
            "requiredValue": is_required,
            "literals": literals,  # For UI rendering
            "classes": classes if classes else [],  # For semantic lookup
            "multipleChoice": multiple
        }
    }
```

#### Post-processing

When user selects a value:
1. CEDAR stores the literal label in @value
2. Background process looks up semantic IRI from classes
3. Additional metadata stored with openMINDS IRI and ontology URI

**Benefits**:
- Best of both worlds: simple UI + semantic richness
- Backward compatible with current implementation
- Gradual migration path

**Challenges**:
- Requires post-processing infrastructure
- More complex data model
- CEDAR may not support dual constraint types

**Timeline**: 2-3 months

### Phase 5: Dynamic Vocabulary Updates (Long-term)

**Goal**: Support dynamic updates from openMINDS

#### Approach

1. **Version Tracking**
```python
class ControlledTermsLoader:
    def __init__(self, version="latest"):
        self.version = version
        self.last_updated = self._check_update_timestamp()

    def check_for_updates(self):
        # Check if openMINDS_instances has new commits
        current = self._get_current_commit()
        latest = self._get_latest_commit()
        return current != latest

    def update_instances(self):
        # Pull latest from git submodule
        subprocess.run(["git", "submodule", "update", "--remote"])
```

2. **Regeneration Pipeline**
```bash
# Automated workflow
1. Check for openMINDS updates (daily cron)
2. If updates found, regenerate CEDAR elements
3. Validate new elements
4. Upload to CEDAR (optional)
5. Notify users of changes
```

3. **Version Management**
```python
element["openminds:sourceVersion"] = {
    "version": "latest",
    "commit": "abc123def456",
    "date": "2025-10-13"
}
```

**Benefits**:
- Always up-to-date with openMINDS
- Automatic synchronization
- Version tracking for reproducibility

**Challenges**:
- Breaking changes in openMINDS
- CEDAR element versioning
- Backward compatibility

**Timeline**: 3-4 months

## Implementation Priority

### High Priority (Weeks 1-4)
1. Semantic IRI preservation in field descriptions (Option A)
2. Code documentation and comments
3. Comprehensive testing suite

### Medium Priority (Months 2-3)
4. InterLex registration for key term types
5. BioPortal value set creation
6. Enhanced validation and error handling

### Low Priority (Months 4-6)
7. Hybrid approach implementation
8. Dynamic update pipeline
9. Advanced provenance tracking

## Resource Requirements

### Phase 1 (IRI Preservation)
- Developer time: 1-2 weeks
- External services: None
- Cost: Minimal

### Phase 2 (InterLex)
- Developer time: 2-4 weeks
- External services: InterLex account, term registration
- Cost: Time for registration process
- Maintenance: Ongoing term management

### Phase 3 (BioPortal)
- Developer time: 3-6 weeks
- External services: BioPortal account, value set creation
- Cost: Free for academic use
- Maintenance: Periodic value set updates

### Phase 4-5 (Advanced Features)
- Developer time: 2-3 months
- Infrastructure: Automated update pipeline
- Testing: Extensive validation
- Cost: Infrastructure for automation

## Success Metrics

### Phase 1
- openMINDS IRIs accessible in field metadata
- No validation failures
- User documentation updated

### Phase 2
- All controlled term types registered in InterLex
- ILX: identifiers mapped to openMINDS IRIs
- CEDAR elements use InterLex URIs

### Phase 3
- BioPortal value sets created for major term types
- Value sets integrated in CEDAR templates
- Autocomplete features functional

### Phase 4-5
- Hybrid approach tested and validated
- Dynamic updates automated
- Full semantic web compliance

## Risk Mitigation

### Risk: CEDAR Validation Changes
- **Mitigation**: Maintain test suite, monitor CEDAR updates
- **Fallback**: Version-specific generators

### Risk: openMINDS Breaking Changes
- **Mitigation**: Version pinning, change detection
- **Fallback**: Manual review process

### Risk: External Service Availability
- **Mitigation**: Caching, local fallbacks
- **Fallback**: Degrade to literal-only mode

### Risk: Semantic Complexity
- **Mitigation**: Phased rollout, user testing
- **Fallback**: Keep simple UI option

## Conclusion

The roadmap balances immediate usability with long-term semantic robustness. Each phase builds on the previous, allowing gradual enhancement without disrupting existing functionality.

Current MVP is production-ready for basic use cases. Semantic enhancements add value for:
- Semantic web integration
- Cross-platform interoperability
- Long-term data sustainability
- Advanced provenance tracking

Choose phases based on specific use case requirements and available resources.
