# Drupal Config Export Command

Export Drupal configuration using Drush.

## Usage

```bash
/drupal/config-export              # Export all config
/drupal/config-export --partial    # Partial export
/drupal/config-export --diff       # Show diff before export
```

## Command Execution

### Read Drupal Configuration

Load configuration from `sessions/sessions-config.json`:
- `drush_command`: Drush command (default: `ddev drush`)

### Check Current Config Status

First, check if there are uncommitted changes:

```bash
{drush_command} config:status
```

### Display Current Status

```
📋 Configuration Status:

   Changes detected:
   ✏️  node.type.article
   ✏️  views.view.articles
   ➕ field.storage.node.field_featured
   ➖ block.block.old_sidebar

   Total: 4 configuration items
```

### Handle --diff Flag

If `--diff` flag provided, show detailed diff:

```bash
{drush_command} config:diff node.type.article
```

Display output and ask for confirmation:

```
📋 Configuration Diff:

[Diff output here]

Proceed with export? (y/n)
```

### Execute Export

```bash
{drush_command} config:export -y
```

### Handle --partial Flag

If `--partial` provided, allow selection:

```
📋 Select configuration items to export:

[ ] node.type.article
[ ] views.view.articles
[x] field.storage.node.field_featured
[ ] block.block.old_sidebar

Export selected items? (y/n)
```

Then export only selected items:

```bash
{drush_command} config:export-single {config_name} -y
```

### Display Results

**On successful export**:
```
✅ Configuration exported successfully

   Exported: 4 items
   Location: config/sync/

   Next steps:
   1. Review changes: git diff config/sync/
   2. Commit changes: git add config/sync/ && git commit -m "Config export"
   3. Push changes: git push
```

**If no changes to export**:
```
✅ Configuration is already synchronized

   No changes detected.
   All configuration is up to date.
```

**On error**:
```
❌ Configuration export failed

   Error: {error_message}

   Troubleshooting:
   - Check Drush is working: {drush_command} status
   - Verify config directory exists: ls -la config/sync/
   - Check file permissions: ls -la config/
```

### Update State

Update `sessions-state.json`:

```json
{
  "drupal": {
    "config_sync_status": "clean"
  }
}
```

## Git Integration

### Auto-commit (if configured)

If `git.auto_commit_config: true` in sessions-config.json:

```bash
git add config/sync/
git commit -m "chore: export Drupal configuration

Exported configuration changes for {task_name}

- Added: {added_count} items
- Modified: {modified_count} items
- Deleted: {deleted_count} items"
```

Display:
```
✅ Configuration exported and committed

   Commit: abc123d
   Files: 4 changed

   Ready to push:
   git push origin {branch}
```

## Examples

### Standard Export

```bash
/drupal/config-export
```

Output:
```
📋 Checking configuration status...

   Changes detected:
   ✏️  node.type.article
   ✏️  views.view.articles

🔄 Exporting configuration...

✅ Configuration exported successfully

   Exported: 2 items
   Location: config/sync/

   Review changes:
   git diff config/sync/
```

### Export with Diff Preview

```bash
/drupal/config-export --diff
```

Output:
```
📋 Configuration Diff:

--- node.type.article
+++ node.type.article
@@ -5,6 +5,7 @@
   dependencies:
     enforced:
       module:
         - node
+        - featured_content
   name: Article
   type: article
+  display_submitted: true

Proceed with export? (y/n): y

🔄 Exporting...

✅ Exported successfully
```

### Partial Export

```bash
/drupal/config-export --partial
```

Output:
```
📋 Select items to export:

[x] 1. node.type.article (Modified)
[ ] 2. views.view.articles (Modified)
[x] 3. field.storage.node.field_featured (New)
[ ] 4. block.block.old_sidebar (Deleted)

Enter numbers (comma-separated) or 'all': 1,3

🔄 Exporting selected items...

✅ Exported 2 items:
   - node.type.article
   - field.storage.node.field_featured
```

## Error Handling

### Drush Not Found

```
❌ Drush not available at: {drush_command}

Install Drush:
  composer require drush/drush

Or update config:
  sessions config drupal set drush_command "drush"
```

### Config Directory Not Writable

```
❌ Cannot write to config directory

   Directory: config/sync/
   Permissions: {permissions}

Fix permissions:
  chmod 755 config/sync/
```

### Export Conflicts

```
⚠️  Configuration conflicts detected

   The following items have conflicts:
   - node.type.article (UUID mismatch)

   Resolve conflicts:
   1. Import current config: drush config:import
   2. Make your changes
   3. Export again: /drupal/config-export
```
