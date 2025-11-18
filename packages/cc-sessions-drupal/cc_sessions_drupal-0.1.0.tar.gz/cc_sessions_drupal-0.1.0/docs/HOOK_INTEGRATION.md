# Hook Integration Guide

This document explains how cc-sessions-drupal integrates with cc-sessions hooks.

## Overview

cc-sessions-drupal extends cc-sessions hooks to add Drupal-specific functionality:

1. **Task Detection** - Recognizes Drupal task patterns
2. **Quality Gate Trigger** - Runs Drupal quality gates on task completion
3. **State Tracking** - Maintains Drupal-specific state
4. **Template Loading** - Loads appropriate Drupal task templates

## Hook Integration Points

### 1. User Message Hook (user_messages.py|.js)

**Enhancement**: Detect task completion for Drupal tasks

```python
# Pseudocode - would be added to user_messages hook

from cc_sessions_drupal.python.task_detector import DrupalTaskDetector

# After detecting task completion phrase
if DrupalTaskDetector.is_drupal_task(current_task_name):
    # Load drupal-quality-gate protocol
    protocol_path = "sessions/extensions/drupal/protocols/drupal-quality-gate.md"
    inject_protocol(protocol_path)
```

**Result**: When user says completion phrase (e.g., "finito") for a Drupal task, the quality gate protocol automatically loads.

### 2. Task Creation Hook (hypothetical)

**Enhancement**: Load Drupal templates for new Drupal tasks

```python
from cc_sessions_drupal.python.task_detector import DrupalTaskDetector

# When new task created with Drupal pattern
if task_name.startswith('@drupal-'):
    metadata = DrupalTaskDetector.get_task_metadata(task_name)

    if metadata['is_drupal']:
        # Load appropriate template
        template_path = f"sessions/extensions/drupal/templates/{metadata['template_path']}"
        populate_task_from_template(template_path, task_file)
```

**Result**: Creating `@drupal-m-featured-block` automatically loads `module-feature.md` template.

### 3. Post Tool Use Hook (post_tool_use.py|.js)

**Enhancement**: Update Drupal state after tool operations

```python
from cc_sessions_drupal.python.drupal_state import DrupalStateManager

# After quality gate tools execute
if tool_name == "Bash" and "phpcs" in command:
    state_manager = DrupalStateManager(sessions_root)
    drupal_state = state_manager.load_drupal_state()

    if phpcs_passed:
        drupal_state.mark_phpcs_run(passed=True)
        state_manager.save_drupal_state(drupal_state)
```

**Result**: State automatically updated when quality gate commands run.

### 4. Sessions Enforce Hook (sessions_enforce.py|.js)

**Enhancement**: Drupal-aware command patterns

```python
# Add Drupal commands to allowed read patterns
DRUPAL_READ_COMMANDS = [
    r'drush\s+(status|config:status|cache:get)',
    r'vendor/bin/phpcs.*--report',
]

# Add to existing READ_PATTERNS
READ_PATTERNS.extend(DRUPAL_READ_COMMANDS)
```

**Result**: Drupal read-only commands allowed in discussion mode.

## Integration Strategy

### Option 1: Direct Integration (Requires cc-sessions modification)

Modify cc-sessions hooks directly to import and use Drupal extensions.

**Pros**:
- Seamless integration
- No user configuration needed

**Cons**:
- Requires modifying cc-sessions core
- Harder to maintain as separate package

### Option 2: Hook Augmentation (Recommended)

cc-sessions-drupal provides wrapper hooks that call original hooks plus Drupal extensions.

**Implementation**:

1. **Installation** copies Drupal hooks to `sessions/hooks/drupal/`
2. **Drupal hooks** call original cc-sessions hooks then add Drupal logic
3. **settings.json** configured to use Drupal hooks

**Example**: `sessions/hooks/drupal/user_messages_drupal.py`

```python
#!/usr/bin/env python3
"""
Drupal-enhanced user messages hook.
Wraps original user_messages hook and adds Drupal functionality.
"""

import sys
import os
from pathlib import Path

# Import original user_messages hook
sys.path.insert(0, str(Path(__file__).parent.parent))
from user_messages import main as original_main

# Import Drupal extensions
from cc_sessions_drupal.python.task_detector import DrupalTaskDetector
from cc_sessions_drupal.python.drupal_state import DrupalStateManager

def drupal_enhancements(result):
    """Add Drupal-specific enhancements after original hook."""
    # Check if this is a Drupal task completion
    sessions_root = Path(os.environ.get('CLAUDE_PROJECT_DIR', '.')) / 'sessions'
    state_manager = DrupalStateManager(sessions_root)

    try:
        state_data = json.loads((sessions_root / 'sessions-state.json').read_text())
        current_task = state_data.get('current_task', {}).get('name')

        if current_task and DrupalTaskDetector.is_drupal_task(current_task):
            # Check if task completion phrase detected
            if should_load_quality_gate():
                # Load Drupal quality gate protocol
                protocol = load_protocol_file('drupal-quality-gate.md')
                print(f"\n{protocol}\n", file=sys.stderr)
    except Exception as e:
        # Fail gracefully - don't break main hook
        pass

    return result

if __name__ == "__main__":
    # Run original hook
    result = original_main()

    # Add Drupal enhancements
    result = drupal_enhancements(result)

    sys.exit(result)
```

### Option 3: MCP Server (Future)

Create cc-sessions-drupal as an MCP server that cc-sessions can call.

**Pros**:
- Clean separation
- No hook modification needed
- Easy updates

**Cons**:
- Requires MCP infrastructure
- More complex architecture

## Installation Process

When cc-sessions-drupal is installed:

1. **Detect cc-sessions**: Verify cc-sessions is installed and get version
2. **Copy Templates**: Install Drupal task templates to `sessions/templates/task-drupal/`
3. **Copy Protocols**: Install protocols to `sessions/protocols/`
4. **Copy Agents**: Install agents to `sessions/agents/`
5. **Copy Commands**: Install slash commands to `sessions/commands/drupal/`
6. **Setup Hooks**: Install wrapper hooks to `sessions/hooks/drupal/`
7. **Update Config**: Add Drupal configuration to `sessions-config.json`
8. **Initialize State**: Add Drupal section to `sessions-state.json`

## Configuration Example

After installation, `sessions-config.json` includes:

```json
{
  "drupal": {
    "version": "11",
    "phpcs_path": "./vendor/bin/phpcs",
    "phpcs_standard": "Drupal,DrupalPractice",
    "config_export_mode": "warn",
    "behat_prompt": true,
    "behat_command": "ddev robo behat",
    "drush_command": "ddev drush",
    "quality_gates": {
      "phpcs": true,
      "security": true,
      "config_check": true,
      "behat": false
    }
  },
  "trigger_phrases": {
    ...existing phrases...
  }
}
```

## State Example

`sessions-state.json` includes:

```json
{
  "drupal": {
    "version": "11",
    "last_phpcs_run": null,
    "config_sync_status": "unknown",
    "active_module": null,
    "active_theme": null,
    "quality_gates_passed": [],
    "pending_tests": false
  },
  ...existing state...
}
```

## Workflow Example

### Drupal Module Task

1. **User creates task**: `sessions tasks start @drupal-m-featured-content-block`
2. **Task Detection**: Hook recognizes Drupal module pattern
3. **Template Load**: `module-feature.md` template populates task file
4. **State Init**: Drupal state initialized for module task
5. **User works**: Implementation in DAIC mode
6. **User completes**: Says "finito"
7. **Quality Gate**: Drupal quality gate protocol loads
8. **PHPCS Run**: Coding standards check executes
9. **Security Scan**: Security patterns validated
10. **Config Check**: Drush config:status checked
11. **Behat Prompt**: User asked about tests
12. **State Update**: Quality gates marked passed
13. **Task Complete**: Allowed to complete if gates pass

## Testing Integration

To test hook integration without full installation:

```bash
# Set environment
export CLAUDE_PROJECT_DIR=/path/to/project

# Test task detection
python -c "
from cc_sessions_drupal.python.task_detector import DrupalTaskDetector
print(DrupalTaskDetector.is_drupal_task('@drupal-m-test'))
print(DrupalTaskDetector.get_task_metadata('@drupal-m-test'))
"

# Test state management
python -c "
from pathlib import Path
from cc_sessions_drupal.python.drupal_state import DrupalStateManager
manager = DrupalStateManager(Path('sessions'))
state = manager.initialize_drupal_state()
print(state.to_dict())
"
```

## Troubleshooting

### Hooks Not Triggering

**Symptom**: Drupal quality gates don't run on task completion

**Solutions**:
1. Check `sessions/hooks/` contains Drupal hooks
2. Verify `.claude/settings.json` references correct hooks
3. Ensure sessions-config.json has Drupal section
4. Check task name follows Drupal pattern (`@drupal-*`)

### Templates Not Loading

**Symptom**: New Drupal tasks don't get templates

**Solutions**:
1. Verify templates exist in `sessions/templates/task-drupal/`
2. Check file permissions on template files
3. Ensure task name matches detection pattern

### State Not Updating

**Symptom**: Quality gate results not persisting

**Solutions**:
1. Check `sessions-state.json` is writable
2. Verify Drupal state section exists in file
3. Check hook can import DrupalStateManager
4. Look for Python import errors in hook output

## Future Enhancements

1. **Automatic Config Export**: Auto-run `drush cex` after module changes
2. **Test Generation**: AI-powered Behat test creation
3. **Performance Monitoring**: Track phpcs execution time, suggest optimizations
4. **Security Dashboard**: Aggregate security findings across multiple tasks
5. **Drupal Update Detection**: Check for Drupal core and contrib updates
