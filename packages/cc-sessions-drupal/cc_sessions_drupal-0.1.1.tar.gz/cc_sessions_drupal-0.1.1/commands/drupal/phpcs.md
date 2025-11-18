# Drupal PHPCS Command

Run Drupal coding standards check using PHP_CodeSniffer.

## Usage

```bash
/drupal/phpcs                              # Check all custom code
/drupal/phpcs modules/custom/my_module     # Check specific path
/drupal/phpcs --fix                        # Auto-fix issues
```

## Command Execution

### Read Drupal Configuration

Load configuration from `sessions/sessions-config.json`:
- `phpcs_path`: Path to phpcs binary (default: `./vendor/bin/phpcs`)
- `phpcs_standard`: Coding standards (default: `Drupal,DrupalPractice`)

### Determine Target Path

1. If path argument provided, use it
2. If current task is Drupal module (`@drupal-m-*`), detect module path
3. If current task is Drupal theme (`@drupal-t-*`), detect theme path
4. Otherwise, use `web/modules/custom` and `web/themes/custom`

### Build PHPCS Command

```bash
{phpcs_path} \
  --standard={phpcs_standard} \
  --extensions=php,module,inc,install,test,profile,theme \
  {path}
```

### Handle --fix Flag

If `--fix` flag provided, use `phpcbf` instead:

```bash
{phpcbf_path} \
  --standard={phpcs_standard} \
  --extensions=php,module,inc,install,test,profile,theme \
  {path}
```

Where `phpcbf_path` is derived from `phpcs_path` by replacing `phpcs` with `phpcbf`.

### Execute Command

Run command using Bash tool and capture output.

### Display Results

**If 0 errors, 0 warnings**:
```
✅ PHPCS: All code follows Drupal coding standards

   Checked: {path}
   Standard: {phpcs_standard}
   Files: {file_count}
```

**If warnings only**:
```
⚠️  PHPCS: {warning_count} warnings found

   {file}:{line} - {warning_message}
   ...

   Run with --fix to auto-correct some issues:
   /drupal/phpcs --fix
```

**If errors found**:
```
❌ PHPCS: {error_count} errors, {warning_count} warnings

   Errors:
   {file}:{line} - {error_message}
   ...

   Warnings:
   {file}:{line} - {warning_message}
   ...

   Fix errors manually, then run:
   /drupal/phpcs
```

**If --fix was used**:
```
🔧 PHPCBF: Auto-fixed {fixed_count} issues

   Remaining:
   ❌ {error_count} errors (manual fix required)
   ⚠️  {warning_count} warnings

   Review changes and run phpcs again:
   /drupal/phpcs
```

### Update State

If check passes (0 errors), update `sessions-state.json`:

```json
{
  "drupal": {
    "last_phpcs_run": "{timestamp}",
    "quality_gates_passed": ["phpcs"]
  }
}
```

## Error Handling

### PHPCS Not Found

```
❌ PHPCS not found at {phpcs_path}

Install Drupal Coder:
  composer require --dev drupal/coder
  ./vendor/bin/phpcs --config-set installed_paths vendor/drupal/coder/coder_sniffer

Update configuration:
  sessions config drupal set phpcs_path ./vendor/bin/phpcs
```

### Path Does Not Exist

```
❌ Path not found: {path}

Specify a valid path:
  /drupal/phpcs web/modules/custom/my_module
```

## Examples

### Check Specific Module

```bash
/drupal/phpcs web/modules/custom/my_module
```

Output:
```
✅ PHPCS: All code follows Drupal coding standards

   Checked: web/modules/custom/my_module
   Standard: Drupal,DrupalPractice
   Files: 12
```

### Auto-Fix Issues

```bash
/drupal/phpcs --fix
```

Output:
```
🔧 PHPCBF: Auto-fixed 8 issues

   Fixed:
   - 5 line spacing issues
   - 2 indentation issues
   - 1 array formatting issue

   Remaining:
   ❌ 2 errors (manual fix required)
   ⚠️  1 warning

   Review changes with git diff
```

### Check All Custom Code

```bash
/drupal/phpcs
```

Output:
```
Running PHPCS on:
  - web/modules/custom
  - web/themes/custom

✅ Modules: 0 errors, 0 warnings (15 files)
⚠️  Themes: 0 errors, 3 warnings (8 files)

Overall: ✅ PASS
```
