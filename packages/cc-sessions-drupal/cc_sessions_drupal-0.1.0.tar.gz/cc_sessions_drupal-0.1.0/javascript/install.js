#!/usr/bin/env node

/**
 * cc-sessions-drupal JavaScript installer
 *
 * This script installs cc-sessions-drupal extension into an existing
 * cc-sessions project by copying templates, protocols, agents, and commands.
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// Colors for console output
const colors = {
  reset: '\x1b[0m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  red: '\x1b[31m',
  blue: '\x1b[34m',
};

function log(message, color = 'reset') {
  console.log(`${colors[color]}${message}${colors.reset}`);
}

function detectProjectRoot() {
  // Check for CLAUDE_PROJECT_DIR environment variable
  if (process.env.CLAUDE_PROJECT_DIR) {
    return process.env.CLAUDE_PROJECT_DIR;
  }

  // Use current working directory
  return process.cwd();
}

function checkCcSessionsInstalled(projectRoot) {
  const sessionsDir = path.join(projectRoot, 'sessions');

  if (!fs.existsSync(sessionsDir)) {
    log('❌ cc-sessions not found', 'red');
    log('   Please install cc-sessions first:', 'yellow');
    log('   npx cc-sessions', 'yellow');
    process.exit(1);
  }

  log(`✅ Found cc-sessions at ${sessionsDir}`, 'green');
  return sessionsDir;
}

function copyDirectory(src, dest) {
  // Create destination directory if it doesn't exist
  if (!fs.existsSync(dest)) {
    fs.mkdirSync(dest, { recursive: true });
  }

  // Read source directory
  const entries = fs.readdirSync(src, { withFileTypes: true });

  for (const entry of entries) {
    const srcPath = path.join(src, entry.name);
    const destPath = path.join(dest, entry.name);

    if (entry.isDirectory()) {
      copyDirectory(srcPath, destPath);
    } else {
      fs.copyFileSync(srcPath, destPath);
    }
  }
}

function installTemplates(extensionRoot, sessionsDir) {
  log('  📄 Installing task templates...', 'blue');

  const srcDir = path.join(extensionRoot, 'templates', 'task-drupal');
  const destDir = path.join(sessionsDir, 'templates', 'task-drupal');

  copyDirectory(srcDir, destDir);

  const templateCount = fs.readdirSync(destDir).length;
  log(`     ✅ Installed ${templateCount} task templates`, 'green');
}

function installProtocols(extensionRoot, sessionsDir) {
  log('  📋 Installing protocols...', 'blue');

  const srcFile = path.join(extensionRoot, 'protocols', 'drupal-quality-gate.md');
  const destDir = path.join(sessionsDir, 'protocols');
  const destFile = path.join(destDir, 'drupal-quality-gate.md');

  if (!fs.existsSync(destDir)) {
    fs.mkdirSync(destDir, { recursive: true });
  }

  fs.copyFileSync(srcFile, destFile);
  log('     ✅ Installed drupal-quality-gate protocol', 'green');
}

function installAgents(extensionRoot, sessionsDir) {
  log('  🤖 Installing specialized agents...', 'blue');

  const agents = ['drupal-architect.md', 'drupal-security-review.md'];
  const srcDir = path.join(extensionRoot, 'agents');
  const destDir = path.join(sessionsDir, 'agents');

  if (!fs.existsSync(destDir)) {
    fs.mkdirSync(destDir, { recursive: true });
  }

  for (const agent of agents) {
    const srcFile = path.join(srcDir, agent);
    const destFile = path.join(destDir, agent);
    fs.copyFileSync(srcFile, destFile);
  }

  log(`     ✅ Installed ${agents.length} Drupal agents`, 'green');
}

function installCommands(extensionRoot, sessionsDir) {
  log('  ⚡ Installing slash commands...', 'blue');

  const srcDir = path.join(extensionRoot, 'commands', 'drupal');
  const destDir = path.join(sessionsDir, 'commands', 'drupal');

  copyDirectory(srcDir, destDir);

  const commandCount = fs.readdirSync(destDir).length;
  log(`     ✅ Installed ${commandCount} Drupal commands`, 'green');
}

function installLibraries(extensionRoot, sessionsDir) {
  log('  📚 Installing JavaScript library...', 'blue');

  const extensionDir = path.join(sessionsDir, 'extensions', 'drupal');
  const destDir = path.join(extensionDir, 'javascript');

  if (!fs.existsSync(destDir)) {
    fs.mkdirSync(destDir, { recursive: true });
  }

  const srcDir = path.join(extensionRoot, 'javascript');
  copyDirectory(srcDir, destDir);

  log('     ✅ Installed JavaScript modules', 'green');
}

function updateConfig(sessionsDir) {
  log('⚙️  Configuring Drupal settings...', 'blue');

  const configFile = path.join(sessionsDir, 'sessions-config.json');

  if (!fs.existsSync(configFile)) {
    log('   ⚠️  sessions-config.json not found, skipping configuration', 'yellow');
    return;
  }

  const config = JSON.parse(fs.readFileSync(configFile, 'utf8'));

  if (config.drupal) {
    log('   ℹ️  Drupal configuration already exists, skipping', 'blue');
    return;
  }

  config.drupal = {
    version: '11',
    phpcs_path: './vendor/bin/phpcs',
    phpcs_standard: 'Drupal,DrupalPractice',
    config_export_mode: 'warn',
    behat_prompt: true,
    behat_command: 'ddev robo behat',
    drush_command: 'ddev drush',
    quality_gates: {
      phpcs: true,
      security: true,
      config_check: true,
      behat: false
    }
  };

  fs.writeFileSync(configFile, JSON.stringify(config, null, 2));
  log('   ✅ Added Drupal configuration', 'green');
}

function initializeState(sessionsDir) {
  log('🔧 Initializing Drupal state...', 'blue');

  const stateFile = path.join(sessionsDir, 'sessions-state.json');

  if (!fs.existsSync(stateFile)) {
    log('   ⚠️  sessions-state.json not found, skipping state initialization', 'yellow');
    return;
  }

  const state = JSON.parse(fs.readFileSync(stateFile, 'utf8'));

  if (state.drupal) {
    log('   ℹ️  Drupal state already exists, skipping', 'blue');
    return;
  }

  state.drupal = {
    version: '11',
    last_phpcs_run: null,
    config_sync_status: 'unknown',
    active_module: null,
    active_theme: null,
    quality_gates_passed: [],
    pending_tests: false
  };

  fs.writeFileSync(stateFile, JSON.stringify(state, null, 2));
  log('   ✅ Initialized Drupal state', 'green');
}

function setupDocumentation(extensionRoot, sessionsDir) {
  log('📖 Setting up documentation...', 'blue');

  const extensionDir = path.join(sessionsDir, 'extensions', 'drupal');
  const docsLink = path.join(extensionDir, 'docs');
  const docsSrc = path.join(extensionRoot, 'docs');

  // Copy docs instead of symlinking (more portable)
  if (!fs.existsSync(extensionDir)) {
    fs.mkdirSync(extensionDir, { recursive: true });
  }

  copyDirectory(docsSrc, docsLink);
  log(`   ✅ Documentation available at ${docsLink}`, 'green');
}

function printNextSteps() {
  log('', 'reset');
  log('✅ Installation complete!', 'green');
  log('', 'reset');
  log('=== Next Steps ===', 'blue');
  log('', 'reset');
  log('1. Configure Drupal settings (optional):', 'reset');
  log('   Edit sessions/sessions-config.json', 'yellow');
  log('', 'reset');
  log('2. Create a Drupal task:', 'reset');
  log('   In Claude Code: mek: @drupal-m-featured-content-block', 'yellow');
  log('', 'reset');
  log('3. Available Drupal commands:', 'reset');
  log('   /drupal/phpcs           # Run coding standards check', 'yellow');
  log('   /drupal/security        # Run security scan', 'yellow');
  log('   /drupal/config-export   # Export configuration', 'yellow');
  log('   /drupal/cache-clear     # Clear caches', 'yellow');
  log('   /drupal/behat           # Run Behat tests', 'yellow');
  log('', 'reset');
  log('4. Documentation:', 'reset');
  log('   sessions/extensions/drupal/docs/HOOK_INTEGRATION.md', 'yellow');
  log('', 'reset');
  log('Happy Drupal development! 🚀', 'green');
}

function main() {
  log('=== cc-sessions-drupal Installation ===', 'blue');
  log('', 'reset');

  // Detect project root
  const projectRoot = detectProjectRoot();
  log(`Using project root: ${projectRoot}`, 'blue');
  log('', 'reset');

  // Check cc-sessions is installed
  const sessionsDir = checkCcSessionsInstalled(projectRoot);
  log('', 'reset');

  // Determine extension root (where this script is running from)
  const extensionRoot = path.join(__dirname, '..');

  log('📦 Installing cc-sessions-drupal components...', 'blue');
  log('', 'reset');

  try {
    // Install components
    installTemplates(extensionRoot, sessionsDir);
    installProtocols(extensionRoot, sessionsDir);
    installAgents(extensionRoot, sessionsDir);
    installCommands(extensionRoot, sessionsDir);
    installLibraries(extensionRoot, sessionsDir);

    log('', 'reset');

    // Configure
    updateConfig(sessionsDir);
    initializeState(sessionsDir);
    setupDocumentation(extensionRoot, sessionsDir);

    log('', 'reset');

    // Print next steps
    printNextSteps();

  } catch (error) {
    log('', 'reset');
    log(`❌ Installation failed: ${error.message}`, 'red');
    process.exit(1);
  }
}

// Run installer
main();
