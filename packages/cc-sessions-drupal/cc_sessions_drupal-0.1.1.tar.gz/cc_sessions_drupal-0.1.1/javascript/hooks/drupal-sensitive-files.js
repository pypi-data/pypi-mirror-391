#!/usr/bin/env node

/**
 * Drupal Sensitive Files Hook
 *
 * Pre-tool hook that blocks Read and Grep access to sensitive files
 * based on patterns defined in sensitive-files.json
 *
 * Exit codes:
 * - 0: Allow access
 * - 1: Block access (hard block)
 * - 2: Warning (soft block, allow with notice)
 */

const fs = require('fs');
const path = require('path');

// Colors for output
const colors = {
  red: '\x1b[31m',
  yellow: '\x1b[33m',
  reset: '\x1b[0m'
};

/**
 * Load sensitive files configuration
 */
function loadSensitiveFilesConfig(projectRoot) {
  const configPath = path.join(projectRoot, 'sessions', 'extensions', 'drupal', 'sensitive-files.json');

  if (!fs.existsSync(configPath)) {
    // No config file, allow access
    return null;
  }

  try {
    const content = fs.readFileSync(configPath, 'utf8');
    return JSON.parse(content);
  } catch (error) {
    // Parse error, allow access but log warning
    console.error(`${colors.yellow}⚠️  Warning: Could not parse sensitive-files.json${colors.reset}`);
    return null;
  }
}

/**
 * Check if file path matches any pattern
 */
function matchesPattern(filePath, patterns) {
  if (!patterns || patterns.length === 0) {
    return false;
  }

  for (const pattern of patterns) {
    // Skip comments
    if (pattern.startsWith('#')) {
      continue;
    }

    try {
      const regex = new RegExp(pattern);
      if (regex.test(filePath)) {
        return true;
      }
    } catch (error) {
      // Invalid regex, skip
      continue;
    }
  }

  return false;
}

/**
 * Check if file is in allowlist
 */
function isAllowlisted(filePath, allowlist) {
  if (!allowlist || allowlist.length === 0) {
    return false;
  }

  return matchesPattern(filePath, allowlist);
}

/**
 * Get all patterns from config
 */
function getAllPatterns(config) {
  const allPatterns = [];

  if (config.patterns) {
    for (const category in config.patterns) {
      const patterns = config.patterns[category];
      if (Array.isArray(patterns)) {
        allPatterns.push(...patterns);
      }
    }
  }

  return allPatterns;
}

/**
 * Check if file access should be blocked
 */
function checkFileAccess(filePath, config) {
  // Check allowlist first (overrides all blocks)
  if (isAllowlisted(filePath, config.allowlist)) {
    return { allowed: true, reason: 'allowlisted' };
  }

  // Check hard block patterns
  const allPatterns = getAllPatterns(config);
  if (matchesPattern(filePath, allPatterns)) {
    return { allowed: false, reason: 'sensitive' };
  }

  // Check warning-only patterns
  if (matchesPattern(filePath, config.warnings_only)) {
    return { allowed: true, reason: 'warning' };
  }

  return { allowed: true, reason: 'clean' };
}

/**
 * Main hook function
 */
function main() {
  // Get project root
  const projectRoot = process.env.CLAUDE_PROJECT_DIR || process.cwd();

  // Load configuration
  const config = loadSensitiveFilesConfig(projectRoot);
  if (!config) {
    // No config or parse error, allow access
    process.exit(0);
  }

  // Get tool information from environment
  const toolName = process.env.TOOL_NAME;
  const toolInput = process.env.TOOL_INPUT;

  // Only check Read and Grep tools
  if (toolName !== 'Read' && toolName !== 'Grep') {
    process.exit(0);
  }

  // Parse tool input to get file path
  let filePath = null;
  try {
    const input = JSON.parse(toolInput || '{}');
    filePath = input.file_path || input.path;
  } catch (error) {
    // Can't parse input, allow access
    process.exit(0);
  }

  if (!filePath) {
    // No file path in input, allow access
    process.exit(0);
  }

  // Check if file access should be blocked
  const result = checkFileAccess(filePath, config);

  if (!result.allowed) {
    // Hard block
    console.error(`${colors.red}🔒 Access Blocked: Sensitive File${colors.reset}`);
    console.error('');
    console.error(`File: ${filePath}`);
    console.error('');
    console.error('This file matches sensitive file patterns and cannot be accessed.');
    console.error('');
    console.error('Sensitive file types blocked:');
    console.error('  • Environment files (.env*)');
    console.error('  • Drupal settings (settings*.php)');
    console.error('  • Credentials (.key, .pem, SSH keys)');
    console.error('');
    console.error('To allow access, add to allowlist in:');
    console.error('  sessions/extensions/drupal/sensitive-files.json');
    console.error('');
    process.exit(1);
  }

  if (result.reason === 'warning') {
    // Soft warning
    console.error(`${colors.yellow}⚠️  Warning: Accessing potentially sensitive file${colors.reset}`);
    console.error(`File: ${filePath}`);
    console.error('');
    process.exit(2);
  }

  // Allow access
  process.exit(0);
}

// Run hook
main();
