# Drupal Cache Clear Command

Clear Drupal caches using Drush.

## Usage

```bash
/drupal/cache-clear          # Clear all caches
/drupal/cache-clear render   # Clear specific cache bin
/drupal/cache-clear --rebuild # Full cache rebuild
```

## Command Execution

### Read Drupal Configuration

Load configuration from `sessions/sessions-config.json`:
- `drush_command`: Drush command (default: `ddev drush`)

### Determine Cache Scope

**If no arguments**: Clear all caches
**If cache bin specified**: Clear specific bin
**If --rebuild flag**: Full cache rebuild

### Cache Bins Available

- `render` - Render cache
- `page` - Page cache
- `dynamic` - Dynamic page cache
- `config` - Configuration cache
- `menu` - Menu cache
- `discovery` - Plugin discovery cache
- `bootstrap` - Bootstrap cache
- `data` - General data cache

### Execute Clear Command

**Clear all caches**:
```bash
{drush_command} cache:rebuild
```

**Clear specific bin**:
```bash
{drush_command} cache:clear {bin}
```

**Full rebuild**:
```bash
{drush_command} cache:rebuild
{drush_command} entity:updates -y
{drush_command} state:set system.maintenance_mode 0
```

### Display Results

**On successful clear**:
```
✅ Caches cleared successfully

   Cleared: All caches
   Time: 2.3s

   Cache bins cleared:
   ✅ Render
   ✅ Page
   ✅ Dynamic
   ✅ Config
   ✅ Menu
   ✅ Discovery
   ✅ Bootstrap
   ✅ Data
```

**For specific bin**:
```
✅ Cache bin cleared: render

   Time: 0.5s
   Items: 1,234 entries removed
```

**On full rebuild**:
```
🔄 Full cache rebuild in progress...

   Step 1/3: Clearing all caches... ✅
   Step 2/3: Updating entity definitions... ✅
   Step 3/3: Verifying site status... ✅

✅ Full rebuild complete

   Time: 4.2s
   Site operational: Yes
```

**On error**:
```
❌ Cache clear failed

   Error: {error_message}

   Troubleshooting:
   - Check Drush status: {drush_command} status
   - Verify database connection
   - Check file permissions on cache directories
```

## Advanced Options

### Selective Cache Clear

```bash
/drupal/cache-clear render,page,menu
```

Output:
```
✅ Selected caches cleared

   Cleared bins:
   ✅ Render (1,234 items)
   ✅ Page (567 items)
   ✅ Menu (89 items)

   Time: 1.2s
```

### Clear with Rebuild

```bash
/drupal/cache-clear --rebuild
```

Output:
```
🔄 Cache rebuild sequence:

   1. Clear all caches... ✅
   2. Rebuild container... ✅
   3. Update entity schemas... ✅
   4. Rebuild router... ✅
   5. Warm up caches... ✅

✅ Complete rebuild finished

   Total time: 5.8s
   Cache status: Warmed
```

## Examples

### Clear All Caches

```bash
/drupal/cache-clear
```

Output:
```
🔄 Clearing all Drupal caches...

✅ Caches cleared successfully

   Cleared: All cache bins
   Time: 2.1s
   Site: Operational
```

### Clear Render Cache

```bash
/drupal/cache-clear render
```

Output:
```
🔄 Clearing render cache...

✅ Render cache cleared

   Items removed: 2,456
   Time: 0.8s
   Memory freed: 45MB
```

### Full Rebuild

```bash
/drupal/cache-clear --rebuild
```

Output:
```
🔄 Performing full cache rebuild...

   Phase 1: Cache clear... ✅ (2.1s)
   Phase 2: Container rebuild... ✅ (1.5s)
   Phase 3: Entity updates... ✅ (0.9s)
   Phase 4: Router rebuild... ✅ (1.2s)

✅ Full rebuild complete

   Total time: 5.7s
   Cache status: Fully rebuilt
   Site status: Operational
```

## Cache Statistics

If `--stats` flag provided:

```bash
/drupal/cache-clear --stats
```

Output:
```
📊 Cache Statistics (before clear):

   Render Cache:
   - Items: 3,456
   - Size: 67MB
   - Hit rate: 87%

   Page Cache:
   - Items: 1,234
   - Size: 23MB
   - Hit rate: 92%

   Config Cache:
   - Items: 567
   - Size: 12MB
   - Hit rate: 98%

🔄 Clearing caches...

✅ Complete

📊 Statistics (after clear):
   Total memory freed: 102MB
   Items removed: 5,257
```

## Integration with Workflows

### After Config Import

Automatically clear caches after config import:

```bash
/drupal/config-export && /drupal/cache-clear
```

### After Code Changes

Clear relevant caches after code deployment:

```bash
/drupal/cache-clear render,discovery
```

### Development Mode

Frequent cache clearing during development:

```bash
# Add to sessions config for quick access
/drupal/cache-clear
```

## Performance Notes

**Cache Clear vs Cache Rebuild**:
- `cache:clear` - Faster, clears cached data
- `cache:rebuild` - Slower, clears and rebuilds everything

**Recommendations**:
- Development: Use `cache:rebuild` for clean state
- Production: Use `cache:clear` for specific bins
- After config changes: Use `cache:rebuild`

## Error Handling

### Drush Not Available

```
❌ Drush not available at: {drush_command}

Install Drush:
  composer require drush/drush

Or update config:
  sessions config drupal set drush_command "drush"
```

### Cache Directory Issues

```
⚠️  Cache directory permissions issue

   Directory: sites/default/files/php
   Owner: {owner}
   Permissions: {permissions}

Fix permissions:
  chmod 775 sites/default/files/php
```

### Database Connection Error

```
❌ Cannot connect to database

   Check database credentials in settings.php
   Verify database server is running:
     ddev status
```
