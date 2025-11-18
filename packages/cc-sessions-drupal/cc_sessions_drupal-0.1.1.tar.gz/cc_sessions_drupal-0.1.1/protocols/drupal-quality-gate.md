# Drupal Quality Gate Protocol

This protocol runs automatically when the user says their configured task completion trigger phrase (e.g., "finito").

## Trigger Conditions

Execute this protocol when:
1. User says task completion phrase
2. Current task name matches `@drupal-*` pattern
3. Drupal configuration exists in sessions-config.json

## Phase 1: Coding Standards Check

### Run PHPCS

Execute phpcs with Drupal coding standards:

```bash
{phpcs_path} --standard={phpcs_standard} --extensions=php,module,inc,install,test,profile,theme {target_path}
```

**Configuration from sessions-config.json**:
- `phpcs_path`: Default `./vendor/bin/phpcs`
- `phpcs_standard`: Default `Drupal,DrupalPractice`
- `target_path`: Detect from task context (module path or theme path)

### Report Results

**If PHPCS passes (0 errors, 0 warnings)**:
```
✅ PHPCS: 0 errors, 0 warnings
```

**If PHPCS has warnings only**:
```
⚠️  PHPCS: 0 errors, X warnings
   Run: {phpcs_command} to see details

📋 Warnings found but not blocking completion.
```

**If PHPCS has errors**:
```
❌ PHPCS: X errors, Y warnings
   Run: {phpcs_command} to see details

🚫 BLOCKING: Cannot complete task until coding standards errors are fixed.
```

**Blocking Rule**: If errors exist, block task completion and stay in implementation mode.

### Update State

Update `sessions-state.json`:
```json
{
  "drupal": {
    "last_phpcs_run": "{timestamp}",
    "quality_gates_passed": ["phpcs"]  // Only if 0 errors
  }
}
```

## Phase 2: Security Validation

### Scan for Security Patterns

Check code for common Drupal security issues:

**SQL Injection Patterns**:
- Raw SQL queries: `db_query()` without placeholders
- Direct `->query()` usage without parameters
- String concatenation in queries

**XSS Vulnerabilities**:
- Unescaped output: `print $variable`
- Missing `#markup` with `Xss::filter()`
- Raw HTML in render arrays without sanitization

**Access Control Issues**:
- Missing access checks in routes
- No `_permission` or `_access` in routing.yml
- Controllers without `checkAccess()`

**Input Validation Issues**:
- Missing form validation handlers
- No input sanitization
- Direct `$_GET`, `$_POST`, `$_REQUEST` usage

### Report Results

**If no security issues found**:
```
✅ Security: No vulnerabilities detected
```

**If security issues found**:
```
⚠️  Security: Potential vulnerabilities detected

   SQL Injection Risks:
   - {file}:{line} - Direct query without placeholders

   XSS Risks:
   - {file}:{line} - Unescaped output

   Access Control:
   - {file}:{line} - Missing access check

📋 Review security issues before completing task.
```

**Non-Blocking**: Security scan warns but doesn't block completion.

### Update State

```json
{
  "drupal": {
    "quality_gates_passed": ["phpcs", "security"]
  }
}
```

## Phase 3: Configuration Export Status

### Check Config Status

Run drush command:
```bash
drush config:status
```

### Parse Output

**If config is clean**:
```
✅ Config: No uncommitted changes
```

**If config has changes**:
```
⚠️  Config: Uncommitted configuration detected

   Changed items:
   - node.type.article
   - views.view.articles

   Run: drush config:export -y
```

### Behavior Based on Config Mode

**Mode: "warn" (default)**:
- Display warning
- Allow completion
- Add reminder to export config

**Mode: "block"**:
- Display warning
- Block completion
- Require `drush cex -y` before proceeding

**Mode: "manual"**:
- No automatic check
- Skip config status

**Configuration from sessions-config.json**:
```json
{
  "drupal": {
    "config_export_mode": "warn"
  }
}
```

## Phase 4: Behat Test Prompt

### Check Behat Configuration

If `behat_prompt: true` in config, ask user:

```
📋 Would you like me to create Behat tests for this feature?
```

### Use AskUserQuestion Tool

```javascript
AskUserQuestion({
  questions: [{
    question: "Would you like me to create Behat tests for this feature?",
    header: "Behat Tests",
    multiSelect: false,
    options: [
      {
        label: "Yes - Comprehensive functional tests",
        description: "Create detailed Behat scenarios covering all user workflows"
      },
      {
        label: "Yes - Basic smoke tests",
        description: "Create minimal tests to verify core functionality"
      },
      {
        label: "No - Skip testing",
        description: "Complete task without creating Behat tests"
      }
    ]
  }]
})
```

### Handle Response

**If user chooses "Yes - Comprehensive"**:
- Stay in implementation mode
- Add Behat test creation to todos
- Create comprehensive test scenarios

**If user chooses "Yes - Basic"**:
- Stay in implementation mode
- Add Behat test creation to todos
- Create minimal smoke tests

**If user chooses "No"**:
- Skip test creation
- Proceed to completion

**If behat_prompt: false**:
- Skip this phase entirely

## Phase 5: Quality Gate Summary

### Display Final Summary

```
🔍 Drupal Quality Gate Results

✅ PHPCS: 0 errors, 0 warnings
✅ Security: No vulnerabilities detected
⚠️  Config: 2 files need export (non-blocking)
📋 Behat: Tests created

Quality gates passed. Task ready for completion.
```

### Update Complete State

```json
{
  "drupal": {
    "quality_gates_passed": ["phpcs", "security", "behat"],
    "config_sync_status": "needs_export"
  }
}
```

## Completion Decision

### Allow Completion If:
- PHPCS has 0 errors (warnings are OK)
- Security scan complete (warnings noted but not blocking)
- Config export mode is "warn" or "manual" (or config is clean)
- Behat prompt handled (if enabled)

### Block Completion If:
- PHPCS has errors
- Config export mode is "block" AND config is dirty

## Error Handling

### PHPCS Not Found

```
❌ PHPCS not found at {phpcs_path}

Install Drupal Coder:
  composer require --dev drupal/coder
  ./vendor/bin/phpcs --config-set installed_paths vendor/drupal/coder/coder_sniffer

Update config:
  sessions config drupal set phpcs_path ./vendor/bin/phpcs
```

### Drush Not Found

```
⚠️  Drush not available - skipping config status check

Install Drush:
  composer require drush/drush
```

### Path Detection Issues

```
⚠️  Could not detect module/theme path from task context

Manually specify path:
  sessions config drupal set target_path web/modules/custom/my_module
```

## Configuration Reference

### sessions-config.json Structure

```json
{
  "drupal": {
    "version": "11",
    "phpcs_path": "./vendor/bin/phpcs",
    "phpcs_standard": "Drupal,DrupalPractice",
    "config_export_mode": "warn",
    "behat_prompt": true,
    "quality_gates": {
      "phpcs": true,
      "security": true,
      "config_check": true,
      "behat": false
    }
  }
}
```

### Disabling Quality Gates

Individual gates can be disabled:

```json
{
  "drupal": {
    "quality_gates": {
      "phpcs": false,        // Skip coding standards check
      "security": false,     // Skip security scan
      "config_check": false, // Skip config status check
      "behat": false         // Skip behat prompt
    }
  }
}
```

## Protocol Exit

After quality gates complete:
- If all gates pass: Allow task completion
- If blocking issues exist: Stay in implementation mode with clear next steps
- Update Drupal state in sessions-state.json
- Return control to user
