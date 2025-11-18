# vyte/__init__.py
"""
Vyte - Rapid Development Tool

Professional API project generator for Python
"""

from .__version__ import __version__

__author__ = "Pablo Domínguez"
__license__ = "MIT"

from .core.config import ProjectConfig
from .core.dependencies import DependencyManager
from .core.generator import ProjectGenerator, quick_generate
from .core.renderer import TemplateRenderer

__all__ = [
    "ProjectConfig",
    "ProjectGenerator",
    "quick_generate",
    "DependencyManager",
    "TemplateRenderer",
]
