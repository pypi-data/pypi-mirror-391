"""
Drupal-specific state management extensions for cc-sessions.

Provides DrupalState class for tracking Drupal-specific metadata
and DrupalConfig for managing Drupal extension configuration.
"""

import json
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any


@dataclass
class DrupalState:
    """
    Drupal-specific state tracking.

    Stored in sessions-state.json under 'drupal' key.
    """
    version: str = "11"
    last_phpcs_run: Optional[str] = None
    config_sync_status: str = "unknown"
    active_module: Optional[str] = None
    active_theme: Optional[str] = None
    quality_gates_passed: List[str] = None
    pending_tests: bool = False

    def __post_init__(self):
        if self.quality_gates_passed is None:
            self.quality_gates_passed = []

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DrupalState':
        """Create DrupalState from dictionary."""
        return cls(**data)

    def mark_phpcs_run(self, passed: bool = True):
        """Mark phpcs as run and update quality gates."""
        self.last_phpcs_run = datetime.now().isoformat()
        if passed and "phpcs" not in self.quality_gates_passed:
            self.quality_gates_passed.append("phpcs")

    def mark_security_scan(self, passed: bool = True):
        """Mark security scan complete."""
        if passed and "security" not in self.quality_gates_passed:
            self.quality_gates_passed.append("security")

    def mark_behat_complete(self):
        """Mark Behat tests as complete."""
        if "behat" not in self.quality_gates_passed:
            self.quality_gates_passed.append("behat")
        self.pending_tests = False

    def reset_quality_gates(self):
        """Reset quality gates for new task."""
        self.quality_gates_passed = []
        self.pending_tests = False
        self.last_phpcs_run = None

    def all_gates_passed(self, required_gates: List[str]) -> bool:
        """Check if all required quality gates have passed."""
        return all(gate in self.quality_gates_passed for gate in required_gates)


@dataclass
class QualityGates:
    """Quality gate toggle configuration."""
    phpcs: bool = True
    security: bool = True
    config_check: bool = True
    behat: bool = False

    def to_dict(self) -> Dict[str, bool]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, bool]) -> 'QualityGates':
        return cls(**data)


@dataclass
class DrupalConfig:
    """
    Drupal extension configuration.

    Stored in sessions-config.json under 'drupal' key.
    """
    version: str = "11"
    phpcs_path: str = "./vendor/bin/phpcs"
    phpcs_standard: str = "Drupal,DrupalPractice"
    config_export_mode: str = "warn"  # warn | block | manual
    behat_prompt: bool = True
    behat_command: str = "ddev robo behat"
    drush_command: str = "ddev drush"
    quality_gates: QualityGates = None

    def __post_init__(self):
        if self.quality_gates is None:
            self.quality_gates = QualityGates()
        elif isinstance(self.quality_gates, dict):
            self.quality_gates = QualityGates.from_dict(self.quality_gates)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        data['quality_gates'] = self.quality_gates.to_dict()
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DrupalConfig':
        """Create DrupalConfig from dictionary."""
        return cls(**data)

    def validate_config_export_mode(self) -> bool:
        """Validate config_export_mode value."""
        return self.config_export_mode in ["warn", "block", "manual"]

    def is_gate_enabled(self, gate_name: str) -> bool:
        """Check if a specific quality gate is enabled."""
        return getattr(self.quality_gates, gate_name, False)


class DrupalStateManager:
    """
    Manager for Drupal state persistence.

    Handles reading/writing Drupal state to sessions-state.json
    and Drupal config to sessions-config.json.
    """

    def __init__(self, sessions_root: Path):
        """
        Initialize state manager.

        Args:
            sessions_root: Path to sessions directory
        """
        self.sessions_root = sessions_root
        self.state_file = sessions_root / "sessions-state.json"
        self.config_file = sessions_root / "sessions-config.json"

    def load_drupal_state(self) -> Optional[DrupalState]:
        """Load Drupal state from sessions-state.json."""
        if not self.state_file.exists():
            return None

        try:
            with open(self.state_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            drupal_data = data.get('drupal')
            if drupal_data:
                return DrupalState.from_dict(drupal_data)
            return None
        except (json.JSONDecodeError, KeyError):
            return None

    def save_drupal_state(self, drupal_state: DrupalState):
        """Save Drupal state to sessions-state.json."""
        if not self.state_file.exists():
            state_data = {}
        else:
            with open(self.state_file, 'r', encoding='utf-8') as f:
                state_data = json.load(f)

        state_data['drupal'] = drupal_state.to_dict()

        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(state_data, f, indent=2)

    def load_drupal_config(self) -> Optional[DrupalConfig]:
        """Load Drupal config from sessions-config.json."""
        if not self.config_file.exists():
            return None

        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            drupal_data = data.get('drupal')
            if drupal_data:
                return DrupalConfig.from_dict(drupal_data)
            return None
        except (json.JSONDecodeError, KeyError):
            return None

    def save_drupal_config(self, drupal_config: DrupalConfig):
        """Save Drupal config to sessions-config.json."""
        if not self.config_file.exists():
            config_data = {}
        else:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)

        config_data['drupal'] = drupal_config.to_dict()

        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2)

    def initialize_drupal_config(self) -> DrupalConfig:
        """Initialize default Drupal configuration if not exists."""
        existing_config = self.load_drupal_config()
        if existing_config:
            return existing_config

        default_config = DrupalConfig()
        self.save_drupal_config(default_config)
        return default_config

    def initialize_drupal_state(self) -> DrupalState:
        """Initialize default Drupal state if not exists."""
        existing_state = self.load_drupal_state()
        if existing_state:
            return existing_state

        default_state = DrupalState()
        self.save_drupal_state(default_state)
        return default_state
