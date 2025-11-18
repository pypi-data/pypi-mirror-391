# cc-sessions-drupal

Drupal-optimized extension for [cc-sessions](https://github.com/GWUDCAP/cc-sessions) that adds quality gates, specialized agents, and workflow enhancements for Drupal 10/11 development.

## Features

### 🎯 Quality Gates
Automatic validation on task completion:
- **PHPCS** - Drupal coding standards enforcement (blocks completion if errors)
- **Security Scan** - SQL injection, XSS, access control validation
- **Config Export** - Configuration sync status checking
- **Behat Tests** - Optional functional test creation prompts

### 📋 Task Templates
Pre-configured structures for common Drupal work:
- **Module Feature** (`@drupal-m-*`) - Custom module development
- **Theme Component** (`@drupal-t-*`) - Theme and frontend work
- **Content Architecture** (`@drupal-a-*`) - Content modeling
- **Migration** (`@drupal-mig-*`) - Data migration tasks
- **Config Management** (`@drupal-c-*`) - Configuration deployment

### 🤖 Specialized Agents
- **drupal-architect** - Architecture planning and content modeling with Context7 integration
- **drupal-security-review** - Comprehensive security audits

### ⚡ Slash Commands
Quick Drupal operations:
- `/drupal/phpcs` - Run coding standards check
- `/drupal/security` - Run security validation
- `/drupal/config-export` - Export configuration
- `/drupal/cache-clear` - Clear all caches
- `/drupal/behat` - Run Behat tests

### 📊 State Tracking
Extended state management for Drupal-specific workflow tracking

## Installation

### Prerequisites

- **cc-sessions** installed and configured
- **Drupal 10 or 11** project
- **PHP 8.1+** with Composer
- **Drush 12+**
- **ddev** or **Lando** (recommended)

### Quick Install

**Python (Recommended):**
```bash
pipx install cc-sessions-drupal
```

**JavaScript/npm:**
```bash
npx cc-sessions-drupal
```

**From Source:**
```bash
git clone https://github.com/gkastanis/cc-sessions-drupal.git
cd cc-sessions-drupal
./install.sh
```

### Verify Installation

```bash
# Check that files were installed
ls sessions/templates/task-drupal/
ls sessions/commands/drupal/
ls sessions/protocols/drupal-quality-gate.md

# Verify configuration
cat sessions/sessions-config.json | grep -A 15 '"drupal"'
```

## Usage

### Creating Drupal Tasks

Use task naming conventions to trigger appropriate templates:

```bash
# Module development
mek: @drupal-m-user-dashboard

# Theme work
mek: @drupal-t-event-card

# Architecture
mek: @drupal-a-member-directory

# Migration
mek: @drupal-mig-legacy-content

# Configuration
mek: @drupal-c-views-export
```

### Quality Gate Workflow

When you complete a task, quality gates run automatically:

```
You: "finito"

Claude:
🔍 Running Drupal quality gates...

Phase 1: Coding Standards
✅ PHPCS: 0 errors, 0 warnings

Phase 2: Security Validation
✅ No SQL injection patterns detected
✅ No XSS vulnerabilities found
✅ Access control checks implemented

Phase 3: Configuration Status
⚠️  Configuration changes detected
   Run: ddev drush cex -y

Phase 4: Functional Tests
📋 Would you like to create Behat tests?
   [Yes] [No]
```

### Using Slash Commands

```bash
# Check coding standards
/drupal/phpcs

# With specific path
/drupal/phpcs web/modules/custom/my_module

# Run security scan
/drupal/security

# Export configuration
/drupal/config-export

# Clear caches
/drupal/cache-clear

# Run Behat tests
/drupal/behat
```

### Example: Building a Custom Module

**1. Create the task:**
```
User: "mek: @drupal-m-newsletter-signup"
```

Claude loads the module template with:
- Module information structure
- Quality gate checklist
- Context manifest
- Work log sections

**2. Start the task:**
```
User: "start^ @drupal-m-newsletter-signup"
```

Claude:
- Creates git branch `drupal/newsletter-signup`
- Loads task context
- Enters discussion mode

**3. Discuss and approve:**
```
User: "I need a block that integrates with Mailchimp API"
Claude: [Discusses architecture, suggests Form API, dependency injection]
User: "yert"
```

**4. Implementation:**
Claude implements:
- Module structure (`*.info.yml`, `*.module`)
- Form class with dependency injection
- Mailchimp integration service
- Configuration schema
- Proper docblocks

**5. Quality gates:**
```
User: "finito"
```

Claude automatically:
1. Runs PHPCS → Validates Drupal standards
2. Security scan → Checks for vulnerabilities
3. Config check → Warns if export needed
4. Behat prompt → Asks about tests

**6. Commit and merge:**
```
User: "commit and create PR"
```

Claude handles git operations and PR creation.

## Configuration

### Drupal Settings

Edit `sessions/sessions-config.json`:

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
  }
}
```

### Configuration Options

**`config_export_mode`:**
- `"warn"` - Notify but don't block completion (default)
- `"block"` - Prevent completion until config exported
- `"manual"` - Only export when explicitly requested

**`quality_gates`:**
- `phpcs: true` - Blocks completion if errors exist
- `security: true` - Warns about vulnerabilities (doesn't block)
- `config_check: true` - Checks configuration status
- `behat: false` - Prompts but doesn't run automatically

**`behat_prompt`:**
- `true` - Ask about creating tests on completion
- `false` - Skip test prompts

### Customizing for Your Environment

**Using Lando instead of ddev:**
```json
{
  "drupal": {
    "drush_command": "lando drush",
    "behat_command": "lando behat"
  }
}
```

**Using native commands (no container):**
```json
{
  "drupal": {
    "drush_command": "drush",
    "behat_command": "vendor/bin/behat"
  }
}
```

**Different PHPCS path:**
```json
{
  "drupal": {
    "phpcs_path": "/usr/local/bin/phpcs"
  }
}
```

## Integration with drupal-claude-code-sub-agent-collective

cc-sessions-drupal complements [drupal-claude-code-sub-agent-collective](https://github.com/gkastanis/drupal-claude-code-sub-agent-collective):

**Your Collective Provides:**
- 14 specialized implementation agents
- Hub-and-spoke routing via orchestrator
- Deep Drupal API expertise
- Quality gate hooks

**cc-sessions-drupal Adds:**
- DAIC workflow enforcement (discuss before code)
- Task-based context management
- Persistent state across sessions
- Todo-based implementation boundaries
- Automatic quality gate protocols

**Together They Provide:**
1. Structured discussion before implementation
2. Specialized agents for complex Drupal work
3. Automatic quality validation
4. Persistent task and state tracking
5. Configuration-driven workflows

## Task Templates Reference

### Module Feature Template
**Pattern:** `@drupal-m-{feature-name}`

Includes:
- Module metadata (name, type, location)
- Quality gates checklist
- Context manifest (files, dependencies)
- Architecture notes (Entity API, Plugin system, Services)
- Performance and security considerations
- Work log with sessions tracking
- Completion checklist

### Theme Component Template
**Pattern:** `@drupal-t-{component-name}`

Includes:
- Component metadata
- Twig template structure
- SCSS/JavaScript organization
- Accessibility checklist
- Browser testing requirements

### Content Architecture Template
**Pattern:** `@drupal-a-{architecture-name}`

Includes:
- Content types and fields
- Taxonomies and entity references
- View modes and form displays
- Migration from existing structure

### Migration Template
**Pattern:** `@drupal-mig-{migration-name}`

Includes:
- Source analysis
- Field mapping
- Migration dependencies
- Rollback procedures

### Config Management Template
**Pattern:** `@drupal-c-{config-name}`

Includes:
- Configuration items scope
- Update hooks
- Deployment procedures
- Testing requirements

## Troubleshooting

### PHPCS Not Found

**Error:** `phpcs: command not found`

**Solution:**
```bash
# Install PHP CodeSniffer
composer require --dev drupal/coder
composer require --dev dealerdirect/phpcodesniffer-composer-installer

# Update config
sessions/sessions-config.json:
  "phpcs_path": "./vendor/bin/phpcs"
```

### Drush Command Fails

**Error:** `drush: command not found`

**Solution:**
```bash
# For ddev
"drush_command": "ddev drush"

# For Lando
"drush_command": "lando drush"

# For native install
"drush_command": "./vendor/bin/drush"
```

### Quality Gates Not Running

**Check:**
1. Task follows naming pattern (`@drupal-*`)
2. Configuration has Drupal section
3. Trigger phrase matches sessions config (`"finito"`)

### Templates Not Loading

**Check:**
```bash
# Verify templates exist
ls sessions/templates/task-drupal/

# Reinstall if missing
pipx reinstall cc-sessions-drupal
# or
npx cc-sessions-drupal
```

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Credits

Built to extend:
- [cc-sessions](https://github.com/GWUDCAP/cc-sessions) by toast
- [drupal-claude-code-sub-agent-collective](https://github.com/gkastanis/drupal-claude-code-sub-agent-collective)

## Support

- **Issues:** [GitHub Issues](https://github.com/gkastanis/cc-sessions-drupal/issues)
- **Discussions:** [GitHub Discussions](https://github.com/gkastanis/cc-sessions-drupal/discussions)

---

**Drupal-Optimized** | **Quality Gates** | **DAIC Workflow** | **cc-sessions Extension**
