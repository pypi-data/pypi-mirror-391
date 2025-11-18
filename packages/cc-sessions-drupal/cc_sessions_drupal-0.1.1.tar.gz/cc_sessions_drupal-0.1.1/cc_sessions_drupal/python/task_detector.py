"""
Drupal task detection and naming convention handler.

Detects Drupal-specific task patterns and loads appropriate templates.
"""

import re
from enum import Enum
from pathlib import Path
from typing import Optional, Dict, Any


class DrupalTaskType(Enum):
    """Drupal task type based on naming convention."""
    MODULE = "module"          # @drupal-m-*
    THEME = "theme"            # @drupal-t-*
    ARCHITECTURE = "arch"      # @drupal-a-*
    CONFIG = "config"          # @drupal-c-*
    MIGRATION = "migration"    # @drupal-mig-*
    UNKNOWN = "unknown"


class DrupalTaskDetector:
    """
    Detects Drupal tasks from naming patterns and loads appropriate templates.
    """

    # Task naming patterns
    TASK_PATTERNS = {
        DrupalTaskType.MODULE: r'^@?drupal-m-',
        DrupalTaskType.THEME: r'^@?drupal-t-',
        DrupalTaskType.ARCHITECTURE: r'^@?drupal-a-',
        DrupalTaskType.CONFIG: r'^@?drupal-c-',
        DrupalTaskType.MIGRATION: r'^@?drupal-mig-',
    }

    # Template file mapping
    TEMPLATE_MAP = {
        DrupalTaskType.MODULE: "task-drupal/module-feature.md",
        DrupalTaskType.THEME: "task-drupal/theme-component.md",
        DrupalTaskType.ARCHITECTURE: "task-drupal/content-architecture.md",
        DrupalTaskType.CONFIG: "task-drupal/config-management.md",
        DrupalTaskType.MIGRATION: "task-drupal/migration.md",
    }

    @classmethod
    def detect_task_type(cls, task_name: str) -> DrupalTaskType:
        """
        Detect Drupal task type from task name.

        Args:
            task_name: Task name (e.g., "@drupal-m-add-featured-field")

        Returns:
            DrupalTaskType enum value
        """
        task_name = task_name.strip().lower()

        for task_type, pattern in cls.TASK_PATTERNS.items():
            if re.match(pattern, task_name):
                return task_type

        return DrupalTaskType.UNKNOWN

    @classmethod
    def is_drupal_task(cls, task_name: str) -> bool:
        """
        Check if task name follows Drupal naming convention.

        Args:
            task_name: Task name to check

        Returns:
            True if task is Drupal-related
        """
        return cls.detect_task_type(task_name) != DrupalTaskType.UNKNOWN

    @classmethod
    def get_template_path(cls, task_type: DrupalTaskType) -> Optional[str]:
        """
        Get template file path for task type.

        Args:
            task_type: DrupalTaskType enum value

        Returns:
            Relative path to template file or None if unknown
        """
        return cls.TEMPLATE_MAP.get(task_type)

    @classmethod
    def extract_feature_name(cls, task_name: str) -> str:
        """
        Extract feature name from task identifier.

        Args:
            task_name: Full task name (e.g., "@drupal-m-add-featured-field")

        Returns:
            Feature name (e.g., "add-featured-field")
        """
        # Remove @ prefix if present
        task_name = task_name.lstrip('@')

        # Find the prefix pattern
        for pattern in cls.TASK_PATTERNS.values():
            match = re.match(pattern, task_name)
            if match:
                # Return everything after the matched prefix
                return task_name[match.end():]

        return task_name

    @classmethod
    def detect_module_name(cls, task_name: str, task_path: Optional[Path] = None) -> Optional[str]:
        """
        Detect module name from task name or path.

        Args:
            task_name: Task name
            task_path: Optional path to task file

        Returns:
            Module machine name or None
        """
        # Try to extract from task name
        feature_name = cls.extract_feature_name(task_name)

        # Convert feature name to module name (snake_case)
        module_name = feature_name.replace('-', '_')

        # If task path provided, try to find module in context
        if task_path and task_path.exists():
            content = task_path.read_text()

            # Look for module name in context manifest
            module_match = re.search(r'web/modules/custom/([a-z_]+)/', content)
            if module_match:
                return module_match.group(1)

        return module_name

    @classmethod
    def detect_theme_name(cls, task_name: str, task_path: Optional[Path] = None) -> Optional[str]:
        """
        Detect theme name from task name or path.

        Args:
            task_name: Task name
            task_path: Optional path to task file

        Returns:
            Theme machine name or None
        """
        # Try to extract from task name
        feature_name = cls.extract_feature_name(task_name)

        # Convert feature name to theme name (snake_case)
        theme_name = feature_name.replace('-', '_')

        # If task path provided, try to find theme in context
        if task_path and task_path.exists():
            content = task_path.read_text()

            # Look for theme name in context manifest
            theme_match = re.search(r'web/themes/custom/([a-z_]+)/', content)
            if theme_match:
                return theme_match.group(1)

        return theme_name

    @classmethod
    def get_task_metadata(cls, task_name: str, task_path: Optional[Path] = None) -> Dict[str, Any]:
        """
        Extract all Drupal task metadata.

        Args:
            task_name: Task name
            task_path: Optional path to task file

        Returns:
            Dictionary with task metadata
        """
        task_type = cls.detect_task_type(task_name)
        feature_name = cls.extract_feature_name(task_name)

        metadata = {
            "task_type": task_type.value,
            "is_drupal": task_type != DrupalTaskType.UNKNOWN,
            "feature_name": feature_name,
            "template_path": cls.get_template_path(task_type),
        }

        if task_type == DrupalTaskType.MODULE:
            metadata["module_name"] = cls.detect_module_name(task_name, task_path)
        elif task_type == DrupalTaskType.THEME:
            metadata["theme_name"] = cls.detect_theme_name(task_name, task_path)

        return metadata

    @classmethod
    def suggest_task_name(cls, description: str, task_type: DrupalTaskType) -> str:
        """
        Suggest a task name based on description and type.

        Args:
            description: Feature description
            task_type: Drupal task type

        Returns:
            Suggested task name
        """
        # Get prefix based on type
        prefix_map = {
            DrupalTaskType.MODULE: "drupal-m-",
            DrupalTaskType.THEME: "drupal-t-",
            DrupalTaskType.ARCHITECTURE: "drupal-a-",
            DrupalTaskType.CONFIG: "drupal-c-",
            DrupalTaskType.MIGRATION: "drupal-mig-",
        }

        prefix = prefix_map.get(task_type, "drupal-")

        # Convert description to kebab-case
        # Remove special characters, convert to lowercase
        clean_desc = re.sub(r'[^a-z0-9\s-]', '', description.lower())

        # Convert spaces to hyphens and collapse multiple hyphens
        kebab = re.sub(r'\s+', '-', clean_desc.strip())
        kebab = re.sub(r'-+', '-', kebab)

        # Limit length
        if len(kebab) > 50:
            kebab = kebab[:50].rstrip('-')

        return f"@{prefix}{kebab}"
