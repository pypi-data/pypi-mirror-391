# Task: @{task-name}

## Task Metadata
- **Type**: Drupal Content Architecture
- **Priority**: {priority}
- **Branch**: drupal/{branch-name}
- **Drupal Version**: {drupal_version}

## Drupal Context

### Architecture Scope
- **Content Types**: {content_type_count}
- **Taxonomy Vocabularies**: {vocabulary_count}
- **Custom Fields**: {field_count}
- **View Modes**: {view_mode_count}
- **Form Displays**: {form_display_count}

### Quality Gates Required
- ✅ Architecture Review: Content model validation
- ✅ Performance: Query and caching considerations
- ✅ Security: Access control and permissions
- ✅ Scalability: Future growth considerations

## Architecture Requirements

### User Story
{architecture_description}

### Goals
- [ ] Goal 1
- [ ] Goal 2
- [ ] Goal 3

## Context Manifest

### Configuration Files
- `config/sync/node.type.*.yml` - Content type definitions
- `config/sync/field.storage.*.yml` - Field storage configurations
- `config/sync/field.field.*.yml` - Field instance configurations
- `config/sync/core.entity_view_display.*.yml` - View mode configurations
- `config/sync/core.entity_form_display.*.yml` - Form display configurations
- `config/sync/taxonomy.vocabulary.*.yml` - Vocabulary definitions

### Related Modules
- Core modules: {core_modules}
- Contrib modules: {contrib_modules}
- Custom modules: {custom_modules}

## Architecture Design

### Content Types

#### {Content Type 1}
**Machine Name**: `{machine_name}`
**Purpose**: {purpose_description}

**Fields**:
| Field Name | Type | Widget | Required | Cardinality | Notes |
|------------|------|--------|----------|-------------|-------|
| field_example | text | textfield | Yes | 1 | Example field |

**View Modes**:
- Default (Full): {display_notes}
- Teaser: {display_notes}
- Custom: {display_notes}

**Form Displays**:
- Default: {form_notes}

### Taxonomy Vocabularies

#### {Vocabulary 1}
**Machine Name**: `{machine_name}`
**Purpose**: {purpose_description}
**Hierarchy**: Flat | Hierarchical
**Usage**: Used by {content_types}

### Entity References

```
[Content Type A] --references--> [Content Type B]
                 --references--> [Taxonomy: Vocab X]
```

### Field Storage Sharing

**Reusable Field Storage**:
- `field_location` - Used by: {bundles}
- `field_contact_email` - Used by: {bundles}
- `field_published_date` - Used by: {bundles}

## Work Log

### Session {session_number} - {date}

#### Architecture Decisions
{content_model_decisions}

#### Performance Considerations
- Page cache: {page_cache_notes}
- Dynamic page cache: {dynamic_cache_notes}
- Query optimization: {query_notes}

#### Security Considerations
- Content permissions: {content_permissions}
- Field-level access: {field_access_notes}

#### Implementation Notes
{implementation_notes}

## Completion Checklist

### Content Model
- [ ] All content types defined
- [ ] All taxonomy vocabularies created
- [ ] All fields created
- [ ] Entity references configured
- [ ] View modes configured

### Configuration Management
- [ ] All configuration exported
- [ ] Configuration committed to git
- [ ] Update hooks created (if needed)

### Documentation
- [ ] Content model diagram created
- [ ] Field usage documented
- [ ] Editorial guidelines written

### Testing
- [ ] Sample content created
- [ ] Workflows tested
- [ ] Display modes verified

## Handoff Notes

### For Implementation Phase
{implementation_handoff_notes}

### Known Limitations
{known_limitations}
