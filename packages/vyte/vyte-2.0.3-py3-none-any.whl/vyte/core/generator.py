"""
Main project generator using Strategy Pattern
"""
from pathlib import Path
from typing import Optional
import shutil
from .config import ProjectConfig
from .renderer import TemplateRenderer, TemplateRegistry
from .dependencies import DependencyManager
from ..strategies.flask_restx import FlaskRestxStrategy
from ..strategies.fastapi import FastAPIStrategy
from ..strategies.django_rest import DjangoRestStrategy


class ProjectGenerator:
    """
    Main project generator
    Orchestrates the project creation using appropriate strategy
    """

    # Strategy registry
    STRATEGIES = {
        'Flask-Restx': FlaskRestxStrategy,
        'FastAPI': FastAPIStrategy,
        'Django-Rest': DjangoRestStrategy,
    }

    def __init__(self, template_dir: Optional[Path] = None):
        """
        Initialize generator

        Args:
            template_dir: Optional custom templates directory
        """
        self.renderer = TemplateRenderer(template_dir)
        self.template_dir = template_dir

    def generate(self, config: ProjectConfig) -> Path:
        """
        Generate a complete project

        Args:
            config: Project configuration

        Returns:
            Path to generated project directory

        Raises:
            ValueError: If framework is not supported
            FileExistsError: If project directory already exists
        """
        # Get project path
        project_path = config.get_output_path()

        # Verify directory doesn't exist
        if project_path.exists():
            raise FileExistsError(
                f"Directory already exists: {project_path}\n"
                "Please choose a different name or delete the existing directory."
            )

        # Create project directory
        project_path.mkdir(parents=True)

        try:
            # Get appropriate strategy
            strategy_class = self.STRATEGIES.get(config.framework)
            if not strategy_class:
                raise ValueError(
                    f"Unsupported framework: {config.framework}\n"
                    f"Supported frameworks: {', '.join(self.STRATEGIES.keys())}"
                )

            # Initialize strategy
            strategy = strategy_class(config, self.renderer)

            # Generate project structure
            self._create_base_structure(project_path, config)

            # Let strategy generate framework-specific files
            strategy.generate_structure(project_path)
            strategy.generate_files(project_path)

            # Generate common files
            self._generate_common_files(project_path, config)

            # Generate dependencies
            self._generate_dependencies(project_path, config)

            # Generate Docker if enabled
            if config.docker_support:
                self._generate_docker_files(project_path, config)

            return project_path

        except Exception as e:
            # Clean up on failure
            if project_path.exists():
                shutil.rmtree(project_path)
            raise e

    def _create_base_structure(self, project_path: Path, config: ProjectConfig):
        """Create basic directory structure"""
        
        # Django tiene su propia estructura, skip base structure
        if config.framework == 'Django-Rest':
            # Solo crear tests/ si tiene testing
            if config.testing_suite:
                tests_dir = project_path / 'tests'
                tests_dir.mkdir(exist_ok=True)
                (tests_dir / '__init__.py').touch()
            return
        
        # Para Flask y FastAPI, crear estructura src/
        dirs = [
            'src',
            'src/models',
            'src/routes',
            'src/services',
            'src/config',
            'src/utils',
        ]

        if config.testing_suite:
            dirs.extend(['tests', 'tests/integration'])

        for dir_name in dirs:
            (project_path / dir_name).mkdir(parents=True, exist_ok=True)

            # Create __init__.py in Python packages
            if dir_name.startswith('src/') or dir_name == 'tests':
                (project_path / dir_name / '__init__.py').touch()

    def _generate_common_files(self, project_path: Path, config: ProjectConfig):
        """Generate files common to all projects"""
        context = config.model_dump_safe()

        # .gitignore
        self.renderer.render_to_file(
            TemplateRegistry.COMMON_TEMPLATES['gitignore'],
            project_path / '.gitignore',
            context
        )

        # .env.example
        self.renderer.render_to_file(
            TemplateRegistry.COMMON_TEMPLATES['env_example'],
            project_path / '.env.example',
            context
        )

        # README.md
        self.renderer.render_to_file(
            TemplateRegistry.COMMON_TEMPLATES['readme'],
            project_path / 'README.md',
            context
        )

        # LICENSE
        self.renderer.render_to_file(
            TemplateRegistry.COMMON_TEMPLATES['license'],
            project_path / 'LICENSE',
            context
        )

        # security.py (if auth enabled)
        if config.auth_enabled:
            # Para Django-Rest, crear en la raíz del proyecto
            if config.framework == 'Django-Rest':
                security_path = project_path / 'security.py'
            else:
                # Para Flask y FastAPI, crear en src/
                security_path = project_path / 'src' / 'security.py'

                self.renderer.render_to_file(
                TemplateRegistry.COMMON_TEMPLATES['security'],
                security_path,
                context
                )

        # pyproject.toml (modern Python packaging)
        self.renderer.render_to_file(
            TemplateRegistry.COMMON_TEMPLATES['pyproject_toml'],
            project_path / 'pyproject.toml',
            context
        )

        # pytest.ini (common test configuration) - place at project root
        if config.testing_suite:
            self.renderer.render_to_file(
                TemplateRegistry.COMMON_TEMPLATES['pytest_ini'],
                project_path / 'pytest.ini',
                context
            )

    def _generate_dependencies(self, project_path: Path, config: ProjectConfig):
        """Generate dependency files"""
        # requirements.txt
        DependencyManager.write_requirements_txt(config, project_path)

        # requirements-dev.txt
        DependencyManager.write_requirements_dev_txt(project_path)


    def _generate_docker_files(self, project_path: Path, config: ProjectConfig):
        """Generate Docker configuration"""
        context = config.model_dump_safe()

        # Dockerfile
        self.renderer.render_to_file(
            TemplateRegistry.COMMON_TEMPLATES['dockerfile'],
            project_path / 'Dockerfile',
            context
        )

        # docker-compose.yml
        self.renderer.render_to_file(
            TemplateRegistry.COMMON_TEMPLATES['docker_compose'],
            project_path / 'docker-compose.yml',
            context
        )

        # .dockerignore
        self.renderer.render_to_file(
            TemplateRegistry.COMMON_TEMPLATES['dockerignore'],
            project_path / '.dockerignore',
            context
        )

    def validate_before_generate(self, config: ProjectConfig) -> tuple[bool, list[str]]:
        """
        Validate configuration before generating

        Returns:
            (is_valid, list_of_errors)
        """
        errors = []

        # Check if templates exist
        templates_exist, missing = TemplateRegistry.validate_templates_exist(
            self.renderer,
            config.framework,
            config.orm
        )

        if not templates_exist:
            errors.append(
                f"Missing templates: {', '.join(missing)}\n"
                "Please ensure all required templates are present."
            )

        # Check for dependency conflicts
        deps = DependencyManager.get_all_dependencies(config)
        warnings = DependencyManager.check_dependency_conflicts(deps)

        if warnings:
            errors.extend(warnings)

        return len(errors) == 0, errors

    def get_generation_summary(self, config: ProjectConfig) -> dict:
        """
        Get summary of what will be generated

        Returns:
            Dictionary with generation details
        """
        deps_info = DependencyManager.get_dependency_info(config)
        templates = TemplateRegistry.get_templates_for_config(
            config.framework,
            config.orm,
            config.auth_enabled,
            config.testing_suite
        )

        return {
            'project_name': config.name,
            'framework': config.framework,
            'orm': config.orm,
            'database': config.database,
            'features': {
                'authentication': config.auth_enabled,
                'docker': config.docker_support,
                'testing': config.testing_suite,
                'git': config.git_init,
            },
            'dependencies': deps_info,
            'templates_count': len(templates),
            'output_path': str(config.get_output_path()),
        }


# Convenience function for quick project generation
def quick_generate(
    name: str,
    framework: str,
    orm: str,
    database: str,
    auth: bool = True,
    docker: bool = True,
    testing: bool = True,
    git: bool = True,
) -> Path:
    """
    Quick project generation with default settings

    Args:
        name: Project name
        framework: Framework to use
        orm: ORM to use
        database: Database type
        auth: Enable authentication
        docker: Include Docker support
        testing: Include testing suite
        git: Initialize git repository

    Returns:
        Path to generated project
    """
    config = ProjectConfig(
        name=name,
        framework=framework,
        orm=orm,
        database=database,
        auth_enabled=auth,
        docker_support=docker,
        testing_suite=testing,
        git_init=git,
    )

    generator = ProjectGenerator()
    return generator.generate(config)
