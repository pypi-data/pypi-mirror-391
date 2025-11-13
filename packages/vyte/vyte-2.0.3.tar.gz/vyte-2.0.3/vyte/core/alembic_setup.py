"""
Alembic setup and configuration automation
"""
# Use explicit encoding string when writing files. Do not import codec module here.
import subprocess
import os
from pathlib import Path


class AlembicConfigurator:
    """
    Handles automatic Alembic initialization and configuration
    """

    @staticmethod
    def setup_alembic(
        project_path: Path,
        project_name: str,
        module_name: str = "src"
    ) -> bool:
        """
        Initialize and configure Alembic for FastAPI + SQLAlchemy projects

        Args:
            project_path: Root path of the project
            project_name: Name of the project (for default DB name)
            module_name: Name of the main module ('src' or 'app')

        Returns:
            True if successful, False otherwise
        """
        original_dir = os.getcwd()

        try:
            os.chdir(project_path)

            # 1. Run alembic init
            print("  🔧 Initializing Alembic...")
            result = subprocess.run(
                ["alembic", "init", "alembic"],
                capture_output=True,
                text=True,
                check=False
            )

            if result.returncode != 0:
                print(f"  ⚠️  Warning: {result.stderr}")
                print("  💡 Note: Alembic will be installed with dependencies")
                return False

            # 2. Configure alembic.ini
            print("  📝 Configuring alembic.ini...")
            AlembicConfigurator._configure_alembic_ini(project_path)

            # 3. Configure env.py
            print("  📝 Configuring alembic/env.py...")
            AlembicConfigurator._configure_env_py(
                project_path,
                project_name,
                module_name
            )

            print("  ✅ Alembic configured successfully")
            return True

        except FileNotFoundError:
            print("  ⚠️  Alembic not found. It will be installed with dependencies.")
            return False
        except (OSError, PermissionError, subprocess.SubprocessError) as e:
            print(f"  ❌ Error setting up Alembic: {e}")
            return False
        finally:
            os.chdir(original_dir)

    @staticmethod
    def _configure_alembic_ini(project_path: Path):
        """Modify alembic.ini to use environment variables"""
        alembic_ini = project_path / "alembic.ini"

        if not alembic_ini.exists():
            return

        with open(alembic_ini, 'r', encoding='utf-8') as f:
            content = f.read()

        # Replace the sqlalchemy.url line
        content = content.replace(
            "sqlalchemy.url = driver://user:pass@localhost/dbname",
            "sqlalchemy.url = "
        )

        with open(alembic_ini, 'w', encoding='utf-8') as f:
            f.write(content)

    @staticmethod
    def _configure_env_py(
        project_path: Path,
        project_name: str,
        module_name: str
    ):
        """Replace env.py with configured version"""
        env_py = project_path / "alembic" / "env.py"

        if not env_py.exists():
            return

        # Generate the configured env.py content
        env_content = f'''import os
import sys
from logging.config import fileConfig
from pathlib import Path

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

# Import Base and models
from {module_name}.database import Base
from {module_name}.models import *  # Import all models

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Get DATABASE_URL from .env and convert for Alembic
database_url = os.getenv("DATABASE_URL", "sqlite:///./{{project_name}}.db")

# Convert async URLs to sync for Alembic
if database_url.startswith("sqlite+aiosqlite"):
    database_url = database_url.replace("sqlite+aiosqlite", "sqlite")
elif database_url.startswith("postgresql+asyncpg"):
    database_url = database_url.replace("postgresql+asyncpg", "postgresql+psycopg2")
elif database_url.startswith("mysql+aiomysql"):
    database_url = database_url.replace("mysql+aiomysql", "mysql+pymysql")

config.set_main_option("sqlalchemy.url", database_url)
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={{"paramstyle": "named"}},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {{}}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
'''

        with open(env_py, 'w', encoding='utf-8') as f:
            f.write(env_content)

    @staticmethod
    def create_alembic_structure_manually(
        project_path: Path,
        project_name: str,
        module_name: str = "src"
    ):
        """
        Create Alembic structure manually without running alembic init
        Use this as fallback if alembic command is not available
        """
        alembic_dir = project_path / "alembic"
        versions_dir = alembic_dir / "versions"

        # Create directories
        alembic_dir.mkdir(exist_ok=True)
        versions_dir.mkdir(exist_ok=True)

        # Create .gitkeep for versions
        (versions_dir / ".gitkeep").touch()

        # Create alembic.ini
        alembic_ini_content = """# A generic, single database configuration.

[alembic]
script_location = alembic
prepend_sys_path = .
path_separator = os

sqlalchemy.url = 

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARNING
handlers = console
qualname =

[logger_sqlalchemy]
level = WARNING
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
"""

        with open(project_path / "alembic.ini", 'w', encoding='utf-8') as f:
            f.write(alembic_ini_content)

        # Create env.py
        AlembicConfigurator._configure_env_py(
            project_path,
            project_name,
            module_name
        )

        # Create script.py.mako
        script_mako_content = '''"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

# revision identifiers, used by Alembic.
revision: str = ${repr(up_revision)}
down_revision: Union[str, None] = ${repr(down_revision)}
branch_labels: Union[str, Sequence[str], None] = ${repr(branch_labels)}
depends_on: Union[str, Sequence[str], None] = ${repr(depends_on)}


def upgrade() -> None:
    ${upgrades if upgrades else "pass"}


def downgrade() -> None:
    ${downgrades if downgrades else "pass"}
'''

        with open(alembic_dir / "script.py.mako", 'w', encoding='utf-8') as f:
            f.write(script_mako_content)

        print("  ✅ Alembic structure created manually")