# Changelog

All notable changes to cc-sessions-drupal will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial packaging for PyPI and npm distribution
- Comprehensive README with usage examples
- Installation guide (INSTALL.md)
- Contributing guidelines (CONTRIBUTING.md)

## [0.1.0] - 2025-11-13

### Added
- Initial release of cc-sessions-drupal
- 5 Drupal task templates:
  - Module feature development
  - Theme component work
  - Content architecture design
  - Data migration
  - Configuration management
- Quality gate protocol with 4 phases:
  - PHPCS coding standards check
  - Security pattern validation
  - Configuration export status
  - Behat test prompts
- 5 Drupal slash commands:
  - `/drupal/phpcs` - Coding standards check
  - `/drupal/security` - Security scan
  - `/drupal/config-export` - Export configuration
  - `/drupal/cache-clear` - Clear caches
  - `/drupal/behat` - Run Behat tests
- 2 specialized agents:
  - drupal-architect - Architecture planning with Context7 integration
  - drupal-security-review - Security compliance validation
- Drupal state tracking:
  - Version tracking
  - PHPCS run history
  - Config sync status
  - Active module context
  - Quality gates status
- Task detection system:
  - Recognizes `@drupal-m-*` (module)
  - Recognizes `@drupal-t-*` (theme)
  - Recognizes `@drupal-a-*` (architecture)
  - Recognizes `@drupal-mig-*` (migration)
  - Recognizes `@drupal-c-*` (config)
- Configuration system:
  - Drupal version support (10/11)
  - PHPCS path configuration
  - Drush command configuration
  - Behat command configuration
  - Quality gate toggles
- Dual-language support:
  - Python implementation
  - JavaScript implementation
  - Feature parity between languages
- Installation script:
  - Auto-detects cc-sessions
  - Copies templates and protocols
  - Installs agents and commands
  - Initializes Drupal state
  - Adds Drupal configuration
- Documentation:
  - Hook integration guide
  - Workflow examples
  - Troubleshooting section

### Integration
- Compatible with cc-sessions v0.3.0+
- Complements drupal-claude-code-sub-agent-collective
- Works with ddev, Lando, Docker, and native installs

### Notes
- Requires Drupal 10 or 11
- Requires PHP 8.1+
- Requires Drush 12+
- Designed for Composer-based Drupal projects

---

## Version History

### Version Numbering

cc-sessions-drupal follows Semantic Versioning:
- **MAJOR** version for incompatible API changes
- **MINOR** version for new functionality in a backward compatible manner
- **PATCH** version for backward compatible bug fixes

### Compatibility Matrix

| cc-sessions-drupal | cc-sessions | Drupal | PHP   |
|-------------------|-------------|--------|-------|
| 0.1.x             | >= 0.3.0    | 10, 11 | 8.1+  |

### Future Plans

See [GitHub Issues](https://github.com/gkastanis/cc-sessions-drupal/issues) for planned features and enhancements.

[Unreleased]: https://github.com/gkastanis/cc-sessions-drupal/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/gkastanis/cc-sessions-drupal/releases/tag/v0.1.0
