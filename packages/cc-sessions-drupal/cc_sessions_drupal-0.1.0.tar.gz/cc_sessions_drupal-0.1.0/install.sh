#!/bin/bash
# cc-sessions-drupal installation script

set -e

echo "=== cc-sessions-drupal Installation ==="
echo ""

# Detect project root (where sessions directory should be)
if [ -z "$CLAUDE_PROJECT_DIR" ]; then
    PROJECT_ROOT="$(pwd)"
    echo "⚠️  CLAUDE_PROJECT_DIR not set, using current directory: $PROJECT_ROOT"
else
    PROJECT_ROOT="$CLAUDE_PROJECT_DIR"
    echo "✅ Using CLAUDE_PROJECT_DIR: $PROJECT_ROOT"
fi

SESSIONS_DIR="$PROJECT_ROOT/sessions"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check if cc-sessions is installed
if [ ! -d "$SESSIONS_DIR" ]; then
    echo "❌ cc-sessions not found at $SESSIONS_DIR"
    echo "   Please install cc-sessions first"
    exit 1
fi

echo "✅ Found cc-sessions at $SESSIONS_DIR"
echo ""

# Create extension directory
EXTENSION_DIR="$SESSIONS_DIR/extensions/drupal"
mkdir -p "$EXTENSION_DIR"

echo "📦 Installing cc-sessions-drupal components..."
echo ""

# Install templates
echo "  📄 Installing task templates..."
mkdir -p "$SESSIONS_DIR/templates/task-drupal"
cp -r "$SCRIPT_DIR/templates/task-drupal/"* "$SESSIONS_DIR/templates/task-drupal/"
echo "     ✅ Installed 5 task templates"

# Install protocols
echo "  📋 Installing protocols..."
mkdir -p "$SESSIONS_DIR/protocols"
cp "$SCRIPT_DIR/protocols/drupal-quality-gate.md" "$SESSIONS_DIR/protocols/"
echo "     ✅ Installed drupal-quality-gate protocol"

# Install agents
echo "  🤖 Installing specialized agents..."
mkdir -p "$SESSIONS_DIR/agents"
cp "$SCRIPT_DIR/agents/drupal-architect.md" "$SESSIONS_DIR/agents/"
cp "$SCRIPT_DIR/agents/drupal-security-review.md" "$SESSIONS_DIR/agents/"
echo "     ✅ Installed 2 Drupal agents"

# Install commands
echo "  ⚡ Installing slash commands..."
mkdir -p "$SESSIONS_DIR/commands/drupal"
cp "$SCRIPT_DIR/commands/drupal/"* "$SESSIONS_DIR/commands/drupal/"
echo "     ✅ Installed 5 Drupal commands"

# Copy library files
echo "  📚 Installing Python library..."
mkdir -p "$EXTENSION_DIR/python"
cp -r "$SCRIPT_DIR/cc_sessions_drupal/"* "$EXTENSION_DIR/python/"
echo "     ✅ Installed Python modules"

echo "  📚 Installing JavaScript library..."
mkdir -p "$EXTENSION_DIR/javascript"
cp -r "$SCRIPT_DIR/javascript/"* "$EXTENSION_DIR/javascript/"
echo "     ✅ Installed JavaScript modules"

# Update sessions-config.json
echo ""
echo "⚙️  Configuring Drupal settings..."

CONFIG_FILE="$SESSIONS_DIR/sessions-config.json"

if [ -f "$CONFIG_FILE" ]; then
    # Check if Drupal section already exists
    if grep -q '"drupal"' "$CONFIG_FILE"; then
        echo "   ℹ️  Drupal configuration already exists, skipping"
    else
        # Add Drupal configuration
        python3 -c "
import json

with open('$CONFIG_FILE', 'r') as f:
    config = json.load(f)

config['drupal'] = {
    'version': '11',
    'phpcs_path': './vendor/bin/phpcs',
    'phpcs_standard': 'Drupal,DrupalPractice',
    'config_export_mode': 'warn',
    'behat_prompt': True,
    'behat_command': 'ddev robo behat',
    'drush_command': 'ddev drush',
    'quality_gates': {
        'phpcs': True,
        'security': True,
        'config_check': True,
        'behat': False
    }
}

with open('$CONFIG_FILE', 'w') as f:
    json.dump(config, f, indent=2)

print('   ✅ Added Drupal configuration')
"
    fi
else
    echo "   ⚠️  sessions-config.json not found, skipping configuration"
fi

# Initialize Drupal state
echo ""
echo "🔧 Initializing Drupal state..."

STATE_FILE="$SESSIONS_DIR/sessions-state.json"

if [ -f "$STATE_FILE" ]; then
    # Check if Drupal state already exists
    if grep -q '"drupal"' "$STATE_FILE"; then
        echo "   ℹ️  Drupal state already exists, skipping"
    else
        # Add Drupal state
        python3 -c "
import json

with open('$STATE_FILE', 'r') as f:
    state = json.load(f)

state['drupal'] = {
    'version': '11',
    'last_phpcs_run': None,
    'config_sync_status': 'unknown',
    'active_module': None,
    'active_theme': None,
    'quality_gates_passed': [],
    'pending_tests': False
}

with open('$STATE_FILE', 'w') as f:
    json.dump(state, f, indent=2)

print('   ✅ Initialized Drupal state')
"
    fi
else
    echo "   ⚠️  sessions-state.json not found, skipping state initialization"
fi

# Create documentation symlink
echo ""
echo "📖 Setting up documentation..."
ln -sf "$SCRIPT_DIR/docs" "$EXTENSION_DIR/docs"
echo "   ✅ Documentation available at $EXTENSION_DIR/docs"

echo ""
echo "✅ Installation complete!"
echo ""
echo "=== Next Steps ==="
echo ""
echo "1. Configure Drupal settings (optional):"
echo "   sessions config drupal set version 10  # If using Drupal 10"
echo "   sessions config drupal set phpcs_path ./vendor/bin/phpcs"
echo ""
echo "2. Create a Drupal task:"
echo "   sessions tasks start @drupal-m-featured-content-block"
echo ""
echo "3. Available Drupal commands:"
echo "   /drupal/phpcs           # Run coding standards check"
echo "   /drupal/security        # Run security scan"
echo "   /drupal/config-export   # Export configuration"
echo "   /drupal/cache-clear     # Clear caches"
echo "   /drupal/behat           # Run Behat tests"
echo ""
echo "4. Documentation:"
echo "   $EXTENSION_DIR/docs/HOOK_INTEGRATION.md"
echo ""
echo "Happy Drupal development! 🚀"
