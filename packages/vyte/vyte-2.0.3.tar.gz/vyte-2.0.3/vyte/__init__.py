# vyte/__init__.py
"""
vyte - Rapid Development Tool

Professional API project generator for Python
"""

__version__ = "2.0.0"
__author__ = "Your Name"
__license__ = "MIT"

from .core.config import ProjectConfig
from .core.generator import ProjectGenerator, quick_generate
from .core.dependencies import DependencyManager
from .core.renderer import TemplateRenderer

__all__ = [
    'ProjectConfig',
    'ProjectGenerator',
    'quick_generate',
    'DependencyManager',
    'TemplateRenderer',
]