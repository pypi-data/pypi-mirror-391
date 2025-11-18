#!/usr/bin/env python3
"""
cc-sessions-drupal Python installer

This script installs cc-sessions-drupal extension into an existing
cc-sessions project by copying templates, protocols, agents, and commands.
"""

import os
import sys
import json
import shutil
from pathlib import Path


def detect_project_root():
    """Detect the project root directory."""
    # Check for CLAUDE_PROJECT_DIR environment variable
    if 'CLAUDE_PROJECT_DIR' in os.environ:
        return Path(os.environ['CLAUDE_PROJECT_DIR'])

    # Use current working directory
    return Path.cwd()


def check_cc_sessions_installed(project_root):
    """Check if cc-sessions is installed."""
    sessions_dir = project_root / 'sessions'

    if not sessions_dir.exists():
        print('❌ cc-sessions not found')
        print('   Please install cc-sessions first:')
        print('   pipx install cc-sessions')
        sys.exit(1)

    print(f'✅ Found cc-sessions at {sessions_dir}')
    return sessions_dir


def copy_directory(src, dest):
    """Recursively copy directory."""
    dest.mkdir(parents=True, exist_ok=True)

    for item in src.iterdir():
        if item.is_dir():
            copy_directory(item, dest / item.name)
        else:
            shutil.copy2(item, dest / item.name)


def install_templates(extension_root, sessions_dir):
    """Install task templates."""
    print('  📄 Installing task templates...')

    src_dir = extension_root / 'templates' / 'task-drupal'
    dest_dir = sessions_dir / 'templates' / 'task-drupal'

    copy_directory(src_dir, dest_dir)

    template_count = len(list(dest_dir.iterdir()))
    print(f'     ✅ Installed {template_count} task templates')


def install_protocols(extension_root, sessions_dir):
    """Install protocols."""
    print('  📋 Installing protocols...')

    src_file = extension_root / 'protocols' / 'drupal-quality-gate.md'
    dest_dir = sessions_dir / 'protocols'
    dest_dir.mkdir(parents=True, exist_ok=True)

    shutil.copy2(src_file, dest_dir / 'drupal-quality-gate.md')
    print('     ✅ Installed drupal-quality-gate protocol')


def install_agents(extension_root, sessions_dir):
    """Install specialized agents."""
    print('  🤖 Installing specialized agents...')

    agents = ['drupal-architect.md', 'drupal-security-review.md']
    src_dir = extension_root / 'agents'
    dest_dir = sessions_dir / 'agents'
    dest_dir.mkdir(parents=True, exist_ok=True)

    for agent in agents:
        shutil.copy2(src_dir / agent, dest_dir / agent)

    print(f'     ✅ Installed {len(agents)} Drupal agents')


def install_commands(extension_root, sessions_dir):
    """Install slash commands."""
    print('  ⚡ Installing slash commands...')

    src_dir = extension_root / 'commands' / 'drupal'
    dest_dir = sessions_dir / 'commands' / 'drupal'

    copy_directory(src_dir, dest_dir)

    command_count = len(list(dest_dir.iterdir()))
    print(f'     ✅ Installed {command_count} Drupal commands')


def install_libraries(extension_root, sessions_dir):
    """Install Python library."""
    print('  📚 Installing Python library...')

    extension_dir = sessions_dir / 'extensions' / 'drupal'
    dest_dir = extension_dir / 'python'
    dest_dir.mkdir(parents=True, exist_ok=True)

    src_dir = extension_root / 'cc_sessions_drupal' / 'python'
    copy_directory(src_dir, dest_dir)

    print('     ✅ Installed Python modules')


def update_config(sessions_dir):
    """Add Drupal configuration."""
    print('⚙️  Configuring Drupal settings...')

    config_file = sessions_dir / 'sessions-config.json'

    if not config_file.exists():
        print('   ⚠️  sessions-config.json not found, skipping configuration')
        return

    with open(config_file, 'r') as f:
        config = json.load(f)

    if 'drupal' in config:
        print('   ℹ️  Drupal configuration already exists, skipping')
        return

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

    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)

    print('   ✅ Added Drupal configuration')


def initialize_state(sessions_dir):
    """Initialize Drupal state."""
    print('🔧 Initializing Drupal state...')

    state_file = sessions_dir / 'sessions-state.json'

    if not state_file.exists():
        print('   ⚠️  sessions-state.json not found, skipping state initialization')
        return

    with open(state_file, 'r') as f:
        state = json.load(f)

    if 'drupal' in state:
        print('   ℹ️  Drupal state already exists, skipping')
        return

    state['drupal'] = {
        'version': '11',
        'last_phpcs_run': None,
        'config_sync_status': 'unknown',
        'active_module': None,
        'active_theme': None,
        'quality_gates_passed': [],
        'pending_tests': False
    }

    with open(state_file, 'w') as f:
        json.dump(state, f, indent=2)

    print('   ✅ Initialized Drupal state')


def setup_documentation(extension_root, sessions_dir):
    """Setup documentation."""
    print('📖 Setting up documentation...')

    extension_dir = sessions_dir / 'extensions' / 'drupal'
    docs_dest = extension_dir / 'docs'
    docs_src = extension_root / 'docs'

    copy_directory(docs_src, docs_dest)
    print(f'   ✅ Documentation available at {docs_dest}')


def print_next_steps():
    """Print next steps."""
    print()
    print('✅ Installation complete!')
    print()
    print('=== Next Steps ===')
    print()
    print('1. Configure Drupal settings (optional):')
    print('   Edit sessions/sessions-config.json')
    print()
    print('2. Create a Drupal task:')
    print('   In Claude Code: mek: @drupal-m-featured-content-block')
    print()
    print('3. Available Drupal commands:')
    print('   /drupal/phpcs           # Run coding standards check')
    print('   /drupal/security        # Run security scan')
    print('   /drupal/config-export   # Export configuration')
    print('   /drupal/cache-clear     # Clear caches')
    print('   /drupal/behat           # Run Behat tests')
    print()
    print('4. Documentation:')
    print('   sessions/extensions/drupal/docs/HOOK_INTEGRATION.md')
    print()
    print('Happy Drupal development! 🚀')


def main():
    """Main installer function."""
    print('=== cc-sessions-drupal Installation ===')
    print()

    # Detect project root
    project_root = detect_project_root()
    print(f'Using project root: {project_root}')
    print()

    # Check cc-sessions is installed
    sessions_dir = check_cc_sessions_installed(project_root)
    print()

    # Determine extension root
    extension_root = Path(__file__).parent.parent

    print('📦 Installing cc-sessions-drupal components...')
    print()

    try:
        # Install components
        install_templates(extension_root, sessions_dir)
        install_protocols(extension_root, sessions_dir)
        install_agents(extension_root, sessions_dir)
        install_commands(extension_root, sessions_dir)
        install_libraries(extension_root, sessions_dir)

        print()

        # Configure
        update_config(sessions_dir)
        initialize_state(sessions_dir)
        setup_documentation(extension_root, sessions_dir)

        print()

        # Print next steps
        print_next_steps()

    except Exception as e:
        print()
        print(f'❌ Installation failed: {e}')
        sys.exit(1)


if __name__ == '__main__':
    main()
