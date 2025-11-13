"""
Configuration module with Pydantic validation
"""
from typing import Literal
from pathlib import Path
from pydantic import BaseModel, Field, field_validator, ConfigDict


# Type definitions for better type safety
Framework = Literal["Flask-Restx", "FastAPI", "Django-Rest"]
ORM = Literal["SQLAlchemy", "TortoiseORM", "Peewee", "DjangoORM"]
Database = Literal["PostgreSQL", "MySQL", "SQLite"]


class ProjectConfig(BaseModel):
    """
    Project configuration with automatic validation

    Attributes:
        name: Project name (lowercase, alphanumeric with - and _)
        framework: Web framework to use
        orm: ORM/ODM to use
        database: Database type
        auth_enabled: Include JWT authentication
        git_init: Initialize git repository
        docker_support: Include Docker configuration
        testing_suite: Include testing infrastructure
    """

    name: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Project name"
    )
    framework: Framework = Field(
        ...,
        description="Web framework"
    )
    orm: ORM = Field(
        ...,
        description="ORM/ODM to use"
    )
    database: Database = Field(
        ...,
        description="Database type"
    )
    auth_enabled: bool = Field(
        default=True,
        description="Include JWT authentication"
    )
    git_init: bool = Field(
        default=True,
        description="Initialize Git repository"
    )
    docker_support: bool = Field(
        default=True,
        description="Include Docker configuration"
    )
    testing_suite: bool = Field(
        default=True,
        description="Include testing infrastructure"
    )

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate project name format"""
        # Convert to lowercase
        v = v.lower().strip()

        # Check if empty after strip
        if not v:
            raise ValueError("Project name cannot be empty")

        # Check if already exists
        if Path(v).exists():
            raise ValueError(f"Directory '{v}' already exists")

        # Check valid characters
        if not all(c.isalnum() or c in '-_' for c in v):
            raise ValueError(
                "Project name can only contain letters, numbers, hyphens and underscores"
            )

        # Cannot start with number
        if v[0].isdigit():
            raise ValueError("Project name cannot start with a number")

        return v

    @field_validator('orm')
    @classmethod
    def validate_orm(cls, v: ORM, info) -> ORM:
        """Validate ORM compatibility with framework"""
        if not info.data:
            return v

        framework = info.data.get('framework')

        # Compatibility rules
        if framework == 'Flask-Restx' and v == 'TortoiseORM':
            raise ValueError(
                "TortoiseORM is not compatible with Flask-Restx "
                "(async/sync mismatch). Use SQLAlchemy or Peewee instead."
            )

        if framework == 'Django-Rest' and v != 'DjangoORM':
            raise ValueError(
                "Django-Rest only works with DjangoORM"
            )

        if framework == 'FastAPI' and v == 'Peewee':
            raise ValueError(
                "Peewee is not recommended for FastAPI. "
                "Use SQLAlchemy (async) or TortoiseORM instead."
            )

        return v

    def get_output_path(self) -> Path:
        """Get the output directory path"""
        return Path.cwd() / self.name

    def is_async_framework(self) -> bool:
        """Check if framework is async-based"""
        return self.framework == "FastAPI"

    def requires_async_driver(self) -> bool:
        """Check if async database driver is needed"""
        return self.is_async_framework() and self.database != "SQLite"

    def get_python_version(self) -> str:
        """Get recommended Python version"""
        return "3.11"

    def get_port(self) -> int:
        """Get default port for framework"""
        return 8000 if self.framework == "FastAPI" else 5300

    def model_dump_safe(self) -> dict:
        """
        Dump model to dict with additional computed fields
        Useful for template rendering
        """
        data = self.model_dump()
        data.update({
            'python_version': self.get_python_version(),
            'port': self.get_port(),
            'is_async': self.is_async_framework(),
            'requires_async_driver': self.requires_async_driver(),
        })
        return data

    model_config = ConfigDict(
        validate_assignment=True,
        use_enum_values=True,
    )


# Compatibility matrix for reference and documentation
COMPATIBILITY_MATRIX = {
    'Flask-Restx': {
        'compatible_orms': ['SQLAlchemy', 'Peewee'],
        'incompatible_orms': ['TortoiseORM', 'DjangoORM'],
        'reason': 'Flask is synchronous, TortoiseORM is async-only',
        'databases': ['PostgreSQL', 'MySQL', 'SQLite'],
        'async_support': False,
    },
    'FastAPI': {
        'compatible_orms': ['SQLAlchemy', 'TortoiseORM'],
        'incompatible_orms': ['Peewee', 'DjangoORM'],
        'reason': 'FastAPI is async, Peewee is sync-only',
        'databases': ['PostgreSQL', 'MySQL', 'SQLite'],
        'async_support': True,
    },
    'Django-Rest': {
        'compatible_orms': ['DjangoORM'],
        'incompatible_orms': ['SQLAlchemy', 'TortoiseORM', 'Peewee'],
        'reason': 'Django-Rest uses Django ORM exclusively',
        'databases': ['PostgreSQL', 'MySQL', 'SQLite'],
        'async_support': False,
    },
}


def get_compatible_orms(framework: Framework) -> list[ORM]:
    """Get list of compatible ORMs for a framework"""
    return COMPATIBILITY_MATRIX[framework]['compatible_orms']


def get_framework_info(framework: Framework) -> dict:
    """Get complete information about a framework"""
    return COMPATIBILITY_MATRIX[framework]


def validate_combination(framework: Framework, orm: ORM) -> tuple[bool, str]:
    """
    Validate if framework and ORM combination is valid

    Returns:
        (is_valid, error_message)
    """
    info = COMPATIBILITY_MATRIX[framework]

    if orm in info['compatible_orms']:
        return True, ""

    if orm in info['incompatible_orms']:
        return False, info['reason']

    return False, f"{orm} is not supported with {framework}"


# Quick validation function for CLI
def quick_validate(
    framework: str,
    orm: str,
    database: str,
    name: str
) -> tuple[bool, list[str]]:
    """
    Quick validation without creating ProjectConfig instance
    Returns: (is_valid, list_of_errors)
    """
    errors = []

    # Validate name
    if not name or not name.strip():
        errors.append("Project name is required")
    elif Path(name).exists():
        errors.append(f"Directory '{name}' already exists")

    # Validate database
    if database not in ["PostgreSQL", "MySQL", "SQLite"]:
        errors.append(f"Invalid database: {database}")

    # Validate combination
    try:
        is_valid, reason = validate_combination(framework, orm)
        if not is_valid:
            errors.append(f"Invalid combination: {reason}")
    except KeyError:
        errors.append(f"Invalid framework or ORM: {framework}, {orm}")

    return len(errors) == 0, errors
