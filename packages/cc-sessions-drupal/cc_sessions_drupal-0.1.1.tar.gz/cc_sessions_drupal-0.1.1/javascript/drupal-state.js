/**
 * Drupal-specific state management extensions for cc-sessions.
 *
 * JavaScript implementation with feature parity to Python version.
 */

const fs = require('fs');
const path = require('path');

/**
 * Drupal-specific state tracking.
 * Stored in sessions-state.json under 'drupal' key.
 */
class DrupalState {
  constructor({
    version = '11',
    last_phpcs_run = null,
    config_sync_status = 'unknown',
    active_module = null,
    active_theme = null,
    quality_gates_passed = [],
    pending_tests = false
  } = {}) {
    this.version = version;
    this.last_phpcs_run = last_phpcs_run;
    this.config_sync_status = config_sync_status;
    this.active_module = active_module;
    this.active_theme = active_theme;
    this.quality_gates_passed = quality_gates_passed;
    this.pending_tests = pending_tests;
  }

  toDict() {
    return {
      version: this.version,
      last_phpcs_run: this.last_phpcs_run,
      config_sync_status: this.config_sync_status,
      active_module: this.active_module,
      active_theme: this.active_theme,
      quality_gates_passed: this.quality_gates_passed,
      pending_tests: this.pending_tests
    };
  }

  static fromDict(data) {
    return new DrupalState(data);
  }

  markPhpcsRun(passed = true) {
    this.last_phpcs_run = new Date().toISOString();
    if (passed && !this.quality_gates_passed.includes('phpcs')) {
      this.quality_gates_passed.push('phpcs');
    }
  }

  markSecurityScan(passed = true) {
    if (passed && !this.quality_gates_passed.includes('security')) {
      this.quality_gates_passed.push('security');
    }
  }

  markBehatComplete() {
    if (!this.quality_gates_passed.includes('behat')) {
      this.quality_gates_passed.push('behat');
    }
    this.pending_tests = false;
  }

  resetQualityGates() {
    this.quality_gates_passed = [];
    this.pending_tests = false;
    this.last_phpcs_run = null;
  }

  allGatesPassed(requiredGates) {
    return requiredGates.every(gate => this.quality_gates_passed.includes(gate));
  }
}

/**
 * Quality gate toggle configuration.
 */
class QualityGates {
  constructor({
    phpcs = true,
    security = true,
    config_check = true,
    behat = false
  } = {}) {
    this.phpcs = phpcs;
    this.security = security;
    this.config_check = config_check;
    this.behat = behat;
  }

  toDict() {
    return {
      phpcs: this.phpcs,
      security: this.security,
      config_check: this.config_check,
      behat: this.behat
    };
  }

  static fromDict(data) {
    return new QualityGates(data);
  }
}

/**
 * Drupal extension configuration.
 * Stored in sessions-config.json under 'drupal' key.
 */
class DrupalConfig {
  constructor({
    version = '11',
    phpcs_path = './vendor/bin/phpcs',
    phpcs_standard = 'Drupal,DrupalPractice',
    config_export_mode = 'warn',
    behat_prompt = true,
    behat_command = 'ddev robo behat',
    drush_command = 'ddev drush',
    quality_gates = null
  } = {}) {
    this.version = version;
    this.phpcs_path = phpcs_path;
    this.phpcs_standard = phpcs_standard;
    this.config_export_mode = config_export_mode;
    this.behat_prompt = behat_prompt;
    this.behat_command = behat_command;
    this.drush_command = drush_command;
    this.quality_gates = quality_gates instanceof QualityGates
      ? quality_gates
      : quality_gates
        ? QualityGates.fromDict(quality_gates)
        : new QualityGates();
  }

  toDict() {
    return {
      version: this.version,
      phpcs_path: this.phpcs_path,
      phpcs_standard: this.phpcs_standard,
      config_export_mode: this.config_export_mode,
      behat_prompt: this.behat_prompt,
      behat_command: this.behat_command,
      drush_command: this.drush_command,
      quality_gates: this.quality_gates.toDict()
    };
  }

  static fromDict(data) {
    return new DrupalConfig(data);
  }

  validateConfigExportMode() {
    return ['warn', 'block', 'manual'].includes(this.config_export_mode);
  }

  isGateEnabled(gateName) {
    return this.quality_gates[gateName] || false;
  }
}

/**
 * Manager for Drupal state persistence.
 * Handles reading/writing Drupal state to sessions-state.json
 * and Drupal config to sessions-config.json.
 */
class DrupalStateManager {
  constructor(sessionsRoot) {
    this.sessionsRoot = sessionsRoot;
    this.stateFile = path.join(sessionsRoot, 'sessions-state.json');
    this.configFile = path.join(sessionsRoot, 'sessions-config.json');
  }

  loadDrupalState() {
    if (!fs.existsSync(this.stateFile)) {
      return null;
    }

    try {
      const data = JSON.parse(fs.readFileSync(this.stateFile, 'utf-8'));
      const drupalData = data.drupal;
      return drupalData ? DrupalState.fromDict(drupalData) : null;
    } catch (error) {
      return null;
    }
  }

  saveDrupalState(drupalState) {
    let stateData = {};
    if (fs.existsSync(this.stateFile)) {
      stateData = JSON.parse(fs.readFileSync(this.stateFile, 'utf-8'));
    }

    stateData.drupal = drupalState.toDict();
    fs.writeFileSync(this.stateFile, JSON.stringify(stateData, null, 2));
  }

  loadDrupalConfig() {
    if (!fs.existsSync(this.configFile)) {
      return null;
    }

    try {
      const data = JSON.parse(fs.readFileSync(this.configFile, 'utf-8'));
      const drupalData = data.drupal;
      return drupalData ? DrupalConfig.fromDict(drupalData) : null;
    } catch (error) {
      return null;
    }
  }

  saveDrupalConfig(drupalConfig) {
    let configData = {};
    if (fs.existsSync(this.configFile)) {
      configData = JSON.parse(fs.readFileSync(this.configFile, 'utf-8'));
    }

    configData.drupal = drupalConfig.toDict();
    fs.writeFileSync(this.configFile, JSON.stringify(configData, null, 2));
  }

  initializeDrupalConfig() {
    const existingConfig = this.loadDrupalConfig();
    if (existingConfig) {
      return existingConfig;
    }

    const defaultConfig = new DrupalConfig();
    this.saveDrupalConfig(defaultConfig);
    return defaultConfig;
  }

  initializeDrupalState() {
    const existingState = this.loadDrupalState();
    if (existingState) {
      return existingState;
    }

    const defaultState = new DrupalState();
    this.saveDrupalState(defaultState);
    return defaultState;
  }
}

module.exports = {
  DrupalState,
  QualityGates,
  DrupalConfig,
  DrupalStateManager
};
