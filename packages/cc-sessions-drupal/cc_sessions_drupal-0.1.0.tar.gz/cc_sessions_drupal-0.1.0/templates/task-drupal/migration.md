# Task: @{task-name}

## Task Metadata
- **Type**: Drupal Content Migration
- **Priority**: {priority}
- **Branch**: drupal/{branch-name}
- **Drupal Version**: {drupal_version}

## Drupal Context

### Migration Information
- **Migration ID**: {migration_id}
- **Source**: {source_system}
- **Destination**: {destination_content_type}
- **Record Count**: {estimated_records}
- **Migration Module**: migrate_plus | custom

### Quality Gates Required
- ✅ Data Validation: Source data integrity
- ✅ Mapping Review: Field mapping correctness
- ✅ Test Migration: Sample data validation
- ✅ Rollback Testing: Verify rollback capability
- ✅ Performance: Migration efficiency

## Migration Requirements

### User Story
{migration_description}

### Goals
- [ ] Migrate {record_count} records from {source}
- [ ] Preserve data integrity
- [ ] Map fields correctly
- [ ] Handle edge cases
- [ ] Provide rollback capability

## Context Manifest

### Files in Scope
- `web/modules/custom/{migration_module}/config/install/migrate_plus.migration.{migration_id}.yml`
- `web/modules/custom/{migration_module}/src/Plugin/migrate/source/{SourcePlugin}.php`
- `web/modules/custom/{migration_module}/src/Plugin/migrate/process/{ProcessPlugin}.php`

### Source Data
- Location: {source_data_location}
- Format: CSV | JSON | Database | XML
- Sample file: {sample_file_path}

## Migration Design

### Source Analysis

**Data Structure**:
| Source Field | Data Type | Sample Value | Notes |
|--------------|-----------|--------------|-------|
| {source_field} | {type} | {sample} | {notes} |

### Field Mapping

| Source Field | Destination Field | Process Plugin | Transformation | Notes |
|--------------|-------------------|----------------|----------------|-------|
| old_title | title | default | None | Direct mapping |
| old_body | body/value | default | None | HTML preserved |

### Migration Dependencies

```
Migration Execution Order:
1. migrate_taxonomy_categories
2. migrate_files_images
3. migrate_main_content
```

## Work Log

### Session {session_number} - {date}

#### Migration Configuration
{migration_config_notes}

#### Testing Results
- Test command: `drush migrate:import {migration_id} --limit=10`
- Records processed: {count}
- Successes: {success_count}
- Failures: {failure_count}

#### Implementation Notes
{implementation_notes}

## Completion Checklist

### Migration Configuration
- [ ] Migration group defined
- [ ] Migration YAML created
- [ ] Source plugin implemented
- [ ] Process plugins implemented

### Field Mapping
- [ ] All source fields mapped
- [ ] Transformations documented
- [ ] Default values defined

### Testing
- [ ] Test migration successful
- [ ] Field values verified
- [ ] Rollback tested

### Documentation
- [ ] Migration documented
- [ ] Field mapping documented
- [ ] Rollback procedure documented

## Migration Commands

```bash
# Import
drush migrate:import {migration_id}

# Status
drush migrate:status

# Rollback
drush migrate:rollback {migration_id}
```

## Handoff Notes

### Production Migration Plan
{production_migration_plan}
