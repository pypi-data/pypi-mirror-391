# Task: @{task-name}

## Task Metadata
- **Type**: Drupal Configuration Management
- **Priority**: {priority}
- **Branch**: drupal/{branch-name}
- **Drupal Version**: {drupal_version}

## Drupal Context

### Configuration Scope
- **Config Items**: {config_item_count}
- **Update Hooks**: {update_hook_count}
- **Deployment Impact**: Low | Medium | High

### Quality Gates Required
- ✅ Config Validation: YAML syntax and schema
- ✅ Dependency Check: Required modules available
- ✅ Import Test: Successful import on fresh environment
- ✅ Update Hook Test: Successful execution

## Configuration Requirements

### User Story
{config_description}

### Goals
- [ ] Export configuration changes
- [ ] Create update hooks if needed
- [ ] Test configuration import
- [ ] Document deployment steps

## Context Manifest

### Configuration Files
- `config/sync/*.yml` - Exported configuration
- `web/modules/custom/{module}/config/install/*.yml` - Default configuration
- `web/modules/custom/{module}/{module}.install` - Update hooks

### Affected Systems
- Content types: {content_types}
- Views: {views}
- Blocks: {blocks}
- Permissions: {permissions}

## Configuration Design

### Configuration Changes

| Config Name | Type | Changes | Reason |
|-------------|------|---------|--------|
| node.type.article | Content Type | Added field_featured | Feature requirement |

### Update Hooks

#### {module_name}_update_10001()
**Purpose**: {update_hook_purpose}

**Actions**:
- Action 1: {description}
- Action 2: {description}

## Work Log

### Session {session_number} - {date}

#### Configuration Export
```bash
ddev drush config:export -y
```

#### Update Hook Development
```php
function {module}_update_10001() {
  // Implementation
  return t('Update completed.');
}
```

#### Testing
```bash
ddev drush config:import -y
ddev drush updatedb -y
```

#### Implementation Notes
{implementation_notes}

## Completion Checklist

### Configuration Export
- [ ] All configuration exported
- [ ] Configuration committed to git
- [ ] No sensitive data in config

### Update Hooks
- [ ] Update hooks created
- [ ] Update hooks tested
- [ ] Documentation complete

### Testing
- [ ] Configuration imports successfully
- [ ] Update hooks execute without errors
- [ ] Site functions normally

## Deployment Procedure

### Pre-Deployment
1. [ ] Backup database
2. [ ] Enable maintenance mode
3. [ ] Clear caches

### Deployment Steps
```bash
git pull origin main
composer install
drush updatedb -y
drush config:import -y
drush cache:rebuild
```

### Rollback Procedure
```bash
drush sql:cli < backup.sql
git reset --hard <previous_commit>
drush cache:rebuild
```

## Handoff Notes

### Deployment Schedule
{deployment_schedule}
