"""
Strategy for FastAPI projects
"""
from pathlib import Path
from .base import BaseStrategy
from ..core.renderer import TemplateRegistry
from ..core.alembic_setup import AlembicConfigurator


class FastAPIStrategy(BaseStrategy):
    """Strategy for generating FastAPI projects"""

    def generate_structure(self, project_path: Path):
        """Create FastAPI-specific directory structure"""
        # Crear src/ primero con su __init__.py
        src_dir = project_path / 'src'
        src_dir.mkdir(exist_ok=True)
        (src_dir / '__init__.py').touch()

        # Crear subdirectorios
        dirs = [
            'src/api',
            'src/schemas',
            'src/crud',
            'src/config',
            'src/models',
        ]

        for dir_name in dirs:
            (project_path / dir_name).mkdir(parents=True, exist_ok=True)
            if dir_name.startswith('src/'):
                (project_path / dir_name / '__init__.py').touch()

        # Tests directory
        if self.config.testing_suite:
            tests_dir = project_path / 'tests'
            tests_dir.mkdir(exist_ok=True)
            (tests_dir / '__init__.py').touch()

    def generate_files(self, project_path: Path):
        """Generate FastAPI specific files"""
        templates = TemplateRegistry.get_templates_for_config(
            self.config.framework,
            self.config.orm,
            self.config.auth_enabled,
            False
        )

        # src/main.py (FastAPI app)
        if 'main' in templates:
            self.renderer.render_to_file(
                templates['main'],
                project_path / 'src' / 'main.py',
                self.context
            )

        # src/database.py or equivalent (for SQLAlchemy)
        if 'database' in templates:
            self.renderer.render_to_file(
                templates['database'],
                project_path / 'src' / 'database.py',
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

        # src/api/routes.py
        if 'routes' in templates:
            self.renderer.render_to_file(
                templates['routes'],
                project_path / 'src' / 'api' / 'routes.py',
                self.context
            )

        # src/schemas/schemas.py
        if 'schemas' in templates:
            self.renderer.render_to_file(
                templates['schemas'],
                project_path / 'src' / 'schemas' / 'schemas.py',
                self.context
            )

        # Security (if auth enabled)
        if self.config.auth_enabled:
            self.renderer.render_to_file(
                TemplateRegistry.COMMON_TEMPLATES['security'],
                project_path / 'src' / 'security.py',
                self.context
            )

        # Generate tests
        if self.config.testing_suite:
            self._generate_tests(project_path)

        # 🔧 Configure Alembic automatically for SQLAlchemy
        if self.config.orm == 'SQLAlchemy':
            self._setup_alembic(project_path)

    def _generate_tests(self, project_path: Path):
        """Generate test files specific to FastAPI + ORM"""
        # Obtener templates de tests específicos
        test_templates = TemplateRegistry.TEST_TEMPLATES.get(
            self.config.framework, {}
        ).get(self.config.orm, {})

        if not test_templates:
            print(f"⚠️  Warning: No test templates found for {self.config.framework} + {self.config.orm}")
            return

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

        # .env.test.example
        if '.env_test' in test_templates:
            self.renderer.render_to_file(
                test_templates['.env_test'],
                project_path / 'tests' / '.env.test.example',
                self.context
            )
        
        # tests/pytest.ini
        if 'pytest_ini' in test_templates:
            self.renderer.render_to_file(
                test_templates['pytest_ini'],
                project_path / 'tests' / 'pytest.ini',
                self.context
            )

    def _setup_alembic(self, project_path: Path):
        """
        Setup and configure Alembic automatically for SQLAlchemy projects
        This runs after all files are generated
        """
        print("\n🔧 Configuring Alembic for database migrations...")

        # Try to run alembic init and configure
        success = AlembicConfigurator.setup_alembic(
            project_path=project_path,
            project_name=self.config.name,
            module_name="src"
        )

        if not success:
            # Fallback: create structure manually if alembic command not available
            print("  📦 Creating Alembic structure manually (alembic not installed yet)...")
            AlembicConfigurator.create_alembic_structure_manually(
                project_path=project_path,
                project_name=self.config.name,
                module_name="src"
            )
            print("  ✅ Alembic structure created. It will be fully configured after installing dependencies.")