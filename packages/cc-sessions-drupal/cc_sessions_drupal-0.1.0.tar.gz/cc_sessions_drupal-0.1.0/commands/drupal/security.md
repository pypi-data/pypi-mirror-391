# Drupal Security Scan Command

Run security validation checks on Drupal code.

## Usage

```bash
/drupal/security                    # Scan all custom code
/drupal/security --module=my_module # Scan specific module
/drupal/security --verbose          # Show detailed findings
```

## Command Execution

### Determine Scan Scope

1. If `--module` flag provided, scan that module
2. If current task is Drupal module (`@drupal-m-*`), scan task module
3. Otherwise, scan all custom modules and themes

### Security Checks Performed

#### 1. SQL Injection Detection

Scan for unsafe database query patterns:

**Patterns to detect**:
- `db_query()` with string concatenation
- Direct `->query()` without placeholders
- `db_select()` with unescaped conditions
- String interpolation in queries

**Example violations**:
```php
// BAD
$result = db_query("SELECT * FROM {users} WHERE name = '$name'");
$result = \Drupal::database()->query("DELETE FROM {node} WHERE nid = " . $nid);

// GOOD
$result = db_query("SELECT * FROM {users} WHERE name = :name", [':name' => $name]);
$result = \Drupal::database()->query("DELETE FROM {node} WHERE nid = :nid", [':nid' => $nid]);
```

#### 2. XSS Vulnerability Detection

Scan for unescaped output:

**Patterns to detect**:
- `print $variable` without sanitization
- Render arrays with `#markup` but no `Xss::filter()`
- Direct `echo` of user input
- `t()` with variables in markup

**Example violations**:
```php
// BAD
print $user_input;
return ['#markup' => $html];
echo $_GET['param'];

// GOOD
print Xss::filter($user_input);
return ['#markup' => Xss::filterAdmin($html)];
echo Html::escape($_GET['param']);
```

#### 3. Access Control Validation

Check for missing access controls:

**Patterns to detect**:
- Routes without `_permission` or `_access`
- Controllers without access checks
- Forms without permission validation
- Entity operations without access checks

**Example violations**:
```yaml
# BAD
my_module.admin_page:
  path: '/admin/my-page'
  defaults:
    _controller: '\Drupal\my_module\Controller\AdminController::page'

# GOOD
my_module.admin_page:
  path: '/admin/my-page'
  defaults:
    _controller: '\Drupal\my_module\Controller\AdminController::page'
  requirements:
    _permission: 'administer my module'
```

#### 4. Input Validation Check

Scan for missing input validation:

**Patterns to detect**:
- Direct `$_GET`, `$_POST`, `$_REQUEST` usage
- Forms without validation handlers
- Missing `#required` on sensitive fields
- No sanitization before storage

**Example violations**:
```php
// BAD
$value = $_GET['id'];
$name = $_POST['name'];

// GOOD
$value = \Drupal::request()->query->get('id');
$name = $form_state->getValue('name');
```

#### 5. File Upload Security

Check file upload handling:

**Patterns to detect**:
- Missing file extension validation
- No file size limits
- Executable file uploads
- Missing virus scanning integration

### Execute Scans

For each check, scan relevant files using grep patterns and AST parsing.

### Display Results

**If no issues found**:
```
✅ Security Scan: No vulnerabilities detected

   Scanned: {file_count} files
   Checks: 5 categories

   ✅ SQL Injection: 0 issues
   ✅ XSS: 0 issues
   ✅ Access Control: 0 issues
   ✅ Input Validation: 0 issues
   ✅ File Upload: 0 issues
```

**If issues found**:
```
⚠️  Security Scan: Vulnerabilities detected

   SQL Injection Risks (2):
   ❌ web/modules/custom/my_module/src/Controller/DataController.php:45
      Unsafe db_query() with string concatenation
      Line: $result = db_query("SELECT * FROM {users} WHERE uid = " . $uid);
      Fix: Use placeholders: db_query("...WHERE uid = :uid", [':uid' => $uid])

   XSS Vulnerabilities (1):
   ❌ web/modules/custom/my_module/src/Controller/PageController.php:32
      Unescaped output using print
      Line: print $user_input;
      Fix: Use Xss::filter($user_input) or Html::escape()

   Access Control Issues (1):
   ⚠️  web/modules/custom/my_module/my_module.routing.yml:5
      Route missing access requirements
      Route: my_module.admin_page
      Fix: Add _permission or _access requirement

   Overall: ⚠️  4 issues found
```

**With --verbose flag**:
```
[Include full code context, line numbers, and detailed remediation steps]
```

### Update State

If no critical issues found, update state:

```json
{
  "drupal": {
    "quality_gates_passed": ["security"]
  }
}
```

## Severity Levels

- 🔴 **Critical**: SQL injection, XSS vulnerabilities
- 🟡 **Warning**: Missing access controls, weak validation
- 🔵 **Info**: Best practice suggestions

## Examples

### Scan Specific Module

```bash
/drupal/security --module=my_module
```

Output:
```
🔍 Scanning: web/modules/custom/my_module

   Files: 12
   Lines: 1,543

✅ No security issues found

   ✅ SQL Injection: 0
   ✅ XSS: 0
   ✅ Access Control: 0
   ✅ Input Validation: 0
```

### Verbose Scan

```bash
/drupal/security --verbose
```

Output:
```
🔍 Detailed Security Scan

SQL Injection Check:
   Scanning for unsafe database queries...
   Files checked: 45
   ❌ Found 2 potential issues

   Issue 1: DataController.php:45
   ────────────────────────────────────────
    43 |   public function getData($uid) {
    44 |     // Get user data
  ❌ 45 |     $result = db_query("SELECT * FROM {users} WHERE uid = " . $uid);
    46 |     return $result;
    47 |   }

   Risk: SQL Injection via unescaped $uid parameter
   Severity: CRITICAL

   Recommendation:
   Use query placeholders to prevent SQL injection:

   $result = db_query(
     "SELECT * FROM {users} WHERE uid = :uid",
     [':uid' => $uid]
   );

[Continue for all findings...]
```

### Scan All Custom Code

```bash
/drupal/security
```

Output:
```
🔍 Scanning all custom code...

   Modules: 5 modules, 67 files
   Themes: 2 themes, 23 files

Results:
   ✅ Modules: 0 critical, 2 warnings
   ✅ Themes: 0 critical, 0 warnings

Warnings:
   ⚠️  my_module/my_module.routing.yml:12
      Missing permission check on admin route

Overall: ✅ PASS (2 minor warnings)
```

## Integration with Quality Gates

Security scan results feed into the Drupal quality gate protocol:

- **Critical issues**: Block task completion
- **Warnings**: Allow completion with notification
- **Info**: Display for awareness only

## Error Handling

### Scan Tools Not Available

```
⚠️  Advanced security scanning requires additional tools

   Install security-checker:
   composer require --dev enlightn/security-checker

   Or continue with basic pattern matching (current):
   Basic checks will still detect common issues.
```

### Large Codebase

```
⏳ Scanning large codebase...

   This may take a few minutes.
   Files: 234
   Estimated time: 2-3 minutes

   [Progress bar]

✅ Scan complete
```
