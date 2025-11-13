from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any
from ..core.config import ProjectConfig
from ..core.renderer import TemplateRenderer

class BaseStrategy(ABC):
    """
    Abstract base class for framework-specific generation strategies
    """

    def __init__(self, config: ProjectConfig, renderer: TemplateRenderer):
        """
        Initialize strategy

        Args:
            config: Project configuration
            renderer: Template renderer instance
        """
        self.config = config
        self.renderer = renderer
        self.context = config.model_dump_safe()

    @abstractmethod
    def generate_structure(self, project_path: Path):
        """
        Generate framework-specific directory structure

        Args:
            project_path: Root path of the project
        """

    @abstractmethod
    def generate_files(self, project_path: Path):
        """
        Generate framework-specific files

        Args:
            project_path: Root path of the project
        """

    def get_context(self) -> Dict[str, Any]:
        """Get template context with additional data"""
        return self.context.copy()
