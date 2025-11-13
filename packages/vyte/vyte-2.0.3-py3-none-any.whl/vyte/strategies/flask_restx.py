"""
Strategy for Flask-Restx projects
"""
from pathlib import Path
from .base import BaseStrategy
from ..core.renderer import TemplateRegistry


class FlaskRestxStrategy(BaseStrategy):
    """Strategy for generating Flask-Restx projects"""

    def generate_structure(self, project_path: Path):
        """Create Flask-specific directory structure"""
        dirs = [
            'src/controllers',
            'migrations',  # For Flask-Migrate
        ]

        for dir_name in dirs:
            (project_path / dir_name).mkdir(parents=True, exist_ok=True)
            if dir_name.startswith('src/'):
                (project_path / dir_name / '__init__.py').touch()

    def generate_files(self, project_path: Path):
        """Generate Flask-Restx specific files"""
        templates = TemplateRegistry.get_templates_for_config(
            self.config.framework,
            self.config.orm,
            self.config.auth_enabled,
            False  # Tests handled separately
        )

        # src/__init__.py (app factory)
        if 'init' in templates:
            self.renderer.render_to_file(
                templates['init'],
                project_path / 'src' / '__init__.py',
                self.context
            )

        # src/extensions.py
        if 'extensions' in templates:
            self.renderer.render_to_file(
                templates['extensions'],
                project_path / 'src' / 'extensions.py',
                self.context
            )

        # src/config/config.py
        if 'config' in templates:
            self.renderer.render_to_file(
                templates['config'],
                project_path / 'src' / 'config' / 'config.py',
                self.context
            )

        # src/models/models.py
        if 'models' in templates:
            self.renderer.render_to_file(
                templates['models'],
                project_path / 'src' / 'models' / 'models.py',
                self.context
            )

        # src/routes/routes_example.py
        if 'routes' in templates:
            self.renderer.render_to_file(
                templates['routes'],
                project_path / 'src' / 'routes' / 'routes_example.py',
                self.context
            )

        # app.py (entry point)
        self.renderer.render_to_file(
            templates['app'],
            project_path / 'app.py',
            self.context
        )

        # Security (if auth enabled)
        self.renderer.render_to_file(
            TemplateRegistry.COMMON_TEMPLATES['security'],
            project_path / 'src' / 'security.py',
            self.context
        )

        # Generate tests
        if self.config.testing_suite:
            self._generate_tests(project_path)

    def _generate_tests(self, project_path: Path):
        """Generate test files specific to Flask-Restx + ORM"""
        # Obtener templates de tests específicos
        test_templates = TemplateRegistry.TEST_TEMPLATES.get(
            self.config.framework, {}
        ).get(self.config.orm, {})

        if not test_templates:
            print(f"Warning: No test templates found for {self.config.framework} + {self.config.orm}")
            return

        #tests/.env.test.example
        if '.env_test' in test_templates:
            self.renderer.render_to_file(
                test_templates['.env_test'],
                project_path / 'tests' / '.env.test.example',
                self.context
            )

        # tests/conftest.py
        if 'conftest' in test_templates:
            self.renderer.render_to_file(
                test_templates['conftest'],
                project_path / 'tests' / 'conftest.py',
                self.context
            )

        # tests/test_api.py
        if 'test_api' in test_templates:
            self.renderer.render_to_file(
                test_templates['test_api'],
                project_path / 'tests' / 'test_api.py',
                self.context
            )

        # tests/test_models.py
        if 'test_models' in test_templates:
            self.renderer.render_to_file(
                test_templates['test_models'],
                project_path / 'tests' / 'test_models.py',
                self.context
            )

        # tests/test_security.py (común)
        if 'test_security' in test_templates:
            self.renderer.render_to_file(
                test_templates['test_security'],
                project_path / 'tests' / 'test_security.py',
                self.context
            )

        # tests/pytest.ini
        if 'pytest_ini' in test_templates:
            self.renderer.render_to_file(
                test_templates['pytest_ini'],
                project_path / 'tests' / 'pytest.ini',
                self.context
            )
