"""
cc-sessions-drupal

Drupal-optimized extension for cc-sessions that adds quality gates,
specialized agents, and workflow enhancements for Drupal 10/11 development.
"""

__version__ = "0.1.0"
__author__ = "cc-sessions-drupal contributors"
__license__ = "MIT"

from .python.drupal_state import DrupalState, DrupalConfig

__all__ = ["DrupalState", "DrupalConfig"]
