# Task: @{task-name}

## Task Metadata
- **Type**: Drupal Module Feature
- **Priority**: {priority}
- **Branch**: drupal/{branch-name}
- **Drupal Version**: {drupal_version}

## Drupal Context

### Module Information
- **Module Name**: {module_name}
- **Module Type**: custom
- **Location**: `web/modules/custom/{module_name}/`

### Quality Gates Required
- ✅ PHPCS: Drupal coding standards compliance
- ✅ Security: SQL injection, XSS, access control validation
- ✅ Functional Tests: Behat tests (on request)
- ✅ Configuration: Config export status

## Feature Requirements

### User Story
{feature_description}

### Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

## Context Manifest

### Files in Scope
- `web/modules/custom/{module_name}/{module_name}.info.yml` - Module definition
- `web/modules/custom/{module_name}/{module_name}.module` - Hook implementations
- `web/modules/custom/{module_name}/{module_name}.services.yml` - Service definitions
- `web/modules/custom/{module_name}/src/` - PHP classes (Controllers, Forms, Plugins, Services)
- `web/modules/custom/{module_name}/config/` - Configuration schemas and defaults
- `web/modules/custom/{module_name}/templates/` - Twig templates
- `behat/features/{feature_name}.feature` - Behat functional tests

### Related Configuration
- `config/sync/*.yml` - Exported Drupal configuration

### Dependencies
- Core modules: {core_dependencies}
- Contrib modules: {contrib_dependencies}
- Custom modules: {custom_dependencies}

## Architecture Notes

### Drupal API Usage
- **Entity API**: {entity_usage_notes}
- **Plugin System**: {plugin_notes}
- **Service Container**: {service_notes}
- **Hooks**: {hook_implementations}

### Performance Considerations
- **Caching**: {caching_strategy}
- **Database**: {database_notes}

### Security Considerations
- **Access Control**: {access_control_notes}
- **Input Validation**: {validation_notes}

## Work Log

### Session {session_number} - {date}

#### Standards Compliance
- [ ] PHPCS: 0 errors, 0 warnings
- [ ] Security review: PASS
- [ ] Behat tests: Created and passing

#### Configuration Management
- [ ] Config exported: `drush cex`
- [ ] Config committed: Yes
- [ ] Update hooks: Created if needed

#### Drupal API Usage
- [ ] Dependency injection: Properly implemented
- [ ] Entity API: Following best practices
- [ ] Hooks: Documented with proper docblocks
- [ ] Services: Registered in services.yml

#### Testing
- [ ] Manual testing: Complete
- [ ] Behat scenarios: {test_count} passing
- [ ] Edge cases: Tested

#### Implementation Notes
{implementation_notes}

## Completion Checklist

### Code Quality
- [ ] All code follows Drupal coding standards
- [ ] No phpcs errors or warnings
- [ ] PHPStan passes (if configured)
- [ ] Code is documented with proper docblocks

### Security
- [ ] No SQL injection vulnerabilities
- [ ] XSS protection implemented
- [ ] Access control checks in place
- [ ] Input validation implemented
- [ ] Output sanitization verified

### Testing
- [ ] Feature works as expected
- [ ] Behat tests created (if requested)
- [ ] Edge cases tested
- [ ] No JavaScript errors in browser console

### Configuration
- [ ] All configuration exported via drush cex
- [ ] Config changes committed to git
- [ ] Update hooks created if needed

### Documentation
- [ ] README.md updated (if needed)
- [ ] API documentation in docblocks
- [ ] Inline comments for complex logic

## Handoff Notes

### For Next Session
{handoff_notes}

### Known Issues
{known_issues}

### Next Steps
{next_steps}
