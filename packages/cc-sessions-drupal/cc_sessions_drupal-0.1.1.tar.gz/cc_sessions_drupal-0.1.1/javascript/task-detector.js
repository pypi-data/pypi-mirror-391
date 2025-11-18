/**
 * Drupal task detection and naming convention handler.
 * JavaScript implementation with feature parity to Python version.
 */

const fs = require('fs');
const path = require('path');

/**
 * Drupal task type enum
 */
const DrupalTaskType = {
  MODULE: 'module',
  THEME: 'theme',
  ARCHITECTURE: 'arch',
  CONFIG: 'config',
  MIGRATION: 'migration',
  UNKNOWN: 'unknown'
};

/**
 * Detects Drupal tasks from naming patterns and loads appropriate templates.
 */
class DrupalTaskDetector {
  /**
   * Task naming patterns
   */
  static TASK_PATTERNS = {
    [DrupalTaskType.MODULE]: /^@?drupal-m-/,
    [DrupalTaskType.THEME]: /^@?drupal-t-/,
    [DrupalTaskType.ARCHITECTURE]: /^@?drupal-a-/,
    [DrupalTaskType.CONFIG]: /^@?drupal-c-/,
    [DrupalTaskType.MIGRATION]: /^@?drupal-mig-/
  };

  /**
   * Template file mapping
   */
  static TEMPLATE_MAP = {
    [DrupalTaskType.MODULE]: 'task-drupal/module-feature.md',
    [DrupalTaskType.THEME]: 'task-drupal/theme-component.md',
    [DrupalTaskType.ARCHITECTURE]: 'task-drupal/content-architecture.md',
    [DrupalTaskType.CONFIG]: 'task-drupal/config-management.md',
    [DrupalTaskType.MIGRATION]: 'task-drupal/migration.md'
  };

  /**
   * Detect Drupal task type from task name.
   */
  static detectTaskType(taskName) {
    const normalizedName = taskName.trim().toLowerCase();

    for (const [taskType, pattern] of Object.entries(this.TASK_PATTERNS)) {
      if (pattern.test(normalizedName)) {
        return taskType;
      }
    }

    return DrupalTaskType.UNKNOWN;
  }

  /**
   * Check if task name follows Drupal naming convention.
   */
  static isDrupalTask(taskName) {
    return this.detectTaskType(taskName) !== DrupalTaskType.UNKNOWN;
  }

  /**
   * Get template file path for task type.
   */
  static getTemplatePath(taskType) {
    return this.TEMPLATE_MAP[taskType] || null;
  }

  /**
   * Extract feature name from task identifier.
   */
  static extractFeatureName(taskName) {
    // Remove @ prefix if present
    let cleanName = taskName.replace(/^@/, '');

    // Find and remove the prefix pattern
    for (const pattern of Object.values(this.TASK_PATTERNS)) {
      const match = cleanName.match(pattern);
      if (match) {
        return cleanName.substring(match[0].length);
      }
    }

    return cleanName;
  }

  /**
   * Detect module name from task name or path.
   */
  static detectModuleName(taskName, taskPath = null) {
    // Extract feature name and convert to snake_case
    const featureName = this.extractFeatureName(taskName);
    let moduleName = featureName.replace(/-/g, '_');

    // If task path provided, try to find module in context
    if (taskPath && fs.existsSync(taskPath)) {
      const content = fs.readFileSync(taskPath, 'utf-8');
      const moduleMatch = content.match(/web\/modules\/custom\/([a-z_]+)\//);
      if (moduleMatch) {
        return moduleMatch[1];
      }
    }

    return moduleName;
  }

  /**
   * Detect theme name from task name or path.
   */
  static detectThemeName(taskName, taskPath = null) {
    // Extract feature name and convert to snake_case
    const featureName = this.extractFeatureName(taskName);
    let themeName = featureName.replace(/-/g, '_');

    // If task path provided, try to find theme in context
    if (taskPath && fs.existsSync(taskPath)) {
      const content = fs.readFileSync(taskPath, 'utf-8');
      const themeMatch = content.match(/web\/themes\/custom\/([a-z_]+)\//);
      if (themeMatch) {
        return themeMatch[1];
      }
    }

    return themeName;
  }

  /**
   * Extract all Drupal task metadata.
   */
  static getTaskMetadata(taskName, taskPath = null) {
    const taskType = this.detectTaskType(taskName);
    const featureName = this.extractFeatureName(taskName);

    const metadata = {
      task_type: taskType,
      is_drupal: taskType !== DrupalTaskType.UNKNOWN,
      feature_name: featureName,
      template_path: this.getTemplatePath(taskType)
    };

    if (taskType === DrupalTaskType.MODULE) {
      metadata.module_name = this.detectModuleName(taskName, taskPath);
    } else if (taskType === DrupalTaskType.THEME) {
      metadata.theme_name = this.detectThemeName(taskName, taskPath);
    }

    return metadata;
  }

  /**
   * Suggest a task name based on description and type.
   */
  static suggestTaskName(description, taskType) {
    // Get prefix based on type
    const prefixMap = {
      [DrupalTaskType.MODULE]: 'drupal-m-',
      [DrupalTaskType.THEME]: 'drupal-t-',
      [DrupalTaskType.ARCHITECTURE]: 'drupal-a-',
      [DrupalTaskType.CONFIG]: 'drupal-c-',
      [DrupalTaskType.MIGRATION]: 'drupal-mig-'
    };

    const prefix = prefixMap[taskType] || 'drupal-';

    // Convert description to kebab-case
    let cleanDesc = description
      .toLowerCase()
      .replace(/[^a-z0-9\s-]/g, '')
      .trim()
      .replace(/\s+/g, '-')
      .replace(/-+/g, '-');

    // Limit length
    if (cleanDesc.length > 50) {
      cleanDesc = cleanDesc.substring(0, 50).replace(/-$/, '');
    }

    return `@${prefix}${cleanDesc}`;
  }
}

module.exports = {
  DrupalTaskType,
  DrupalTaskDetector
};
