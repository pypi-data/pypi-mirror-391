"""
Strategy for Django-Rest projects
"""
from pathlib import Path
from .base import BaseStrategy
from ..core.renderer import TemplateRegistry


class DjangoRestStrategy(BaseStrategy):
    """Strategy for generating Django-Rest projects"""

    def generate_structure(self, project_path: Path):
        """Create Django-specific directory structure ONLY"""
        app_name = self.config.name.replace('-', '_')

        # SOLO directorios específicos de Django (NO src/)
        dirs = [
            f'{app_name}',                          # Main Django app
            f'{app_name}/migrations',               # Database migrations
            f'{app_name}/management',               # Custom management commands
            f'{app_name}/management/commands',      # Command modules
        ]

        for dir_name in dirs:
            dir_path = project_path / dir_name
            dir_path.mkdir(parents=True, exist_ok=True)
            
            # Create __init__.py for Python packages
            (dir_path / '__init__.py').touch()
        
        # Create initial migration __init__.py
        (project_path / app_name / 'migrations' / '__init__.py').touch()

    def generate_files(self, project_path: Path):
        """Generate Django-Rest specific files ONLY"""
        app_name = self.config.name.replace('-', '_')
        
        # Get templates for this configuration
        templates = TemplateRegistry.get_templates_for_config(
            self.config.framework,
            self.config.orm,
            self.config.auth_enabled,
            self.config.testing_suite
        )
        
        if not templates:
            raise ValueError(
                f"No templates found for {self.config.framework} + {self.config.orm}"
            )

        # Core Django files
        self._generate_core_files(project_path, app_name, templates)
        
        # API files (models, serializers, views, permissions)
        self._generate_api_files(project_path, app_name, templates)
        
        # WSGI and ASGI
        self._generate_deployment_files(project_path, app_name)
        
        # Django management script
        self._generate_manage_py(project_path, app_name)
        
        # Test files (solo configuración Django)
        if self.config.testing_suite:
            self._generate_test_configs(project_path, templates)

    def _generate_core_files(self, project_path: Path, app_name: str, templates: dict):
        """Generate core Django configuration files"""
        
        # settings.py
        if 'settings' in templates:
            self.renderer.render_to_file(
                templates['settings'],
                project_path / app_name / 'settings.py',
                self.context
            )
        
        # urls.py
        if 'urls' in templates:
            self.renderer.render_to_file(
                templates['urls'],
                project_path / app_name / 'urls.py',
                self.context
            )
        
        # apps.py
        self._generate_apps_py(project_path, app_name)

    def _generate_api_files(self, project_path: Path, app_name: str, templates: dict):
        """Generate API-related files"""
        
        # models.py - EN LA RAÍZ DEL APP (NO en /api)
        if 'models' in templates:
            self.renderer.render_to_file(
                templates['models'],
                project_path / app_name / 'models.py',  # ✅ Aquí, no en /api
                self.context
            )
        
        # serializers.py
        if 'serializers' in templates:
            self.renderer.render_to_file(
                templates['serializers'],
                project_path / app_name / 'serializers.py',
                self.context
            )
        
        # views.py
        if 'views' in templates:
            self.renderer.render_to_file(
                templates['views'],
                project_path / app_name / 'views.py',
                self.context
            )
        
        # permissions.py (if auth enabled)
        if self.config.auth_enabled and 'permissions' in templates:
            self.renderer.render_to_file(
                templates['permissions'],
                project_path / app_name / 'permissions.py',
                self.context
            )

    def _generate_apps_py(self, project_path: Path, app_name: str):
        """Generate Django apps.py configuration"""
        apps_content = f'''"""
App configuration for {app_name}
"""
from django.apps import AppConfig


class {self._to_pascal_case(app_name)}Config(AppConfig):
    """Configuration for {app_name} app"""
    default_auto_field = 'django.db.models.BigAutoField'
    name = '{app_name}'
    verbose_name = '{app_name.replace("_", " ").title()}'
'''
        (project_path / app_name / 'apps.py').write_text(apps_content)

    def _generate_deployment_files(self, project_path: Path, app_name: str):
        """Generate WSGI and ASGI files for deployment"""
        
        # wsgi.py
        wsgi_content = f'''"""
WSGI config for {app_name} project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/stable/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', '{app_name}.settings')

application = get_wsgi_application()
'''
        (project_path / app_name / 'wsgi.py').write_text(wsgi_content)
        
        # asgi.py
        asgi_content = f'''"""
ASGI config for {app_name} project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/stable/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', '{app_name}.settings')

application = get_asgi_application()
'''
        (project_path / app_name / 'asgi.py').write_text(asgi_content)

    def _generate_manage_py(self, project_path: Path, app_name: str):
        """Generate manage.py file"""
        
        manage_py_content = f'''#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', '{app_name}.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
'''
        manage_py_path = project_path / 'manage.py'
        manage_py_path.write_text(manage_py_content)
        manage_py_path.chmod(0o755)  # Make executable

    def _generate_test_configs(self, project_path: Path, templates: dict):
        """Generate Django-specific test configuration files"""
        
        # pytest.ini (Django-specific config)
        if 'pytest_ini' in templates:
            self.renderer.render_to_file(
                templates['pytest_ini'],
                project_path / 'pytest.ini',
                self.context
            )
        
        # conftest.py (Django fixtures)
        if 'conftest' in templates:
            self.renderer.render_to_file(
                templates['conftest'],
                project_path / 'tests' / 'conftest.py',
                self.context
            )
        
        # test_api.py
        if 'test_api' in templates:
            self.renderer.render_to_file(
                templates['test_api'],
                project_path / 'tests' / 'test_api.py',
                self.context
            )
        
        # test_models.py
        if 'test_models' in templates:
            self.renderer.render_to_file(
                templates['test_models'],
                project_path / 'tests' / 'test_models.py',
                self.context
            )

    @staticmethod
    def _to_pascal_case(text: str) -> str:
        """Convert snake_case to PascalCase"""
        return ''.join(word.capitalize() for word in text.split('_'))