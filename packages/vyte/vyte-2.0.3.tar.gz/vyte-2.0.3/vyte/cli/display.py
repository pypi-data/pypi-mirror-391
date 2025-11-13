# vyte/cli/display.py
"""
Display utilities using Rich
"""
import time
from pathlib import Path
from typing import List
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.markdown import Markdown

from ..core.config import ProjectConfig
from ..core.generator import ProjectGenerator

console = Console()


def show_welcome():
    """Show welcome banner"""
    banner = """
    ╔═══════════════════════════════════════════╗
    ║                                           ║
    ║        🚀  vyte v2.0                      ║
    ║     Rapid Development Tool                ║
    ║                                           ║
    ║   Professional API Generator for Python   ║
    ║                                           ║
    ╚═══════════════════════════════════════════╝
    """

    console.print(Panel.fit(
        banner,
        border_style="cyan",
        padding=(0, 2)
    ))


def show_summary(config: ProjectConfig):
    """Show project configuration summary"""
    table = Table(
        title="📋 Project Configuration",
        show_header=False,
        border_style="cyan"
    )
    table.add_column("Setting", style="cyan", width=20)
    table.add_column("Value", style="green")

    table.add_row("Project Name", config.name)
    table.add_row("Framework", config.framework)
    table.add_row("ORM", config.orm)
    table.add_row("Database", config.database)
    table.add_row("Authentication", "✅ Enabled" if config.auth_enabled else "❌ Disabled")
    table.add_row("Docker", "✅ Included" if config.docker_support else "❌ Not included")
    table.add_row("Testing", "✅ Included" if config.testing_suite else "❌ Not included")
    table.add_row("Git Init", "✅ Yes" if config.git_init else "❌ No")
    table.add_row("Output Path", str(config.get_output_path()))

    console.print("\n")
    console.print(table)
    console.print("\n")


def show_generation_progress(
    generator: ProjectGenerator,
    config: ProjectConfig
) -> Path:
    """
    Show generation progress with spinner

    Returns:
        Path to generated project
    """
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        console=console
    ) as progress:

        task = progress.add_task("🔨 Generating project...", total=100)

        # Start generation
        progress.update(task, advance=10, description="📁 Creating directories...")
        time.sleep(0.3)

        progress.update(task, advance=20, description="📝 Generating files...")
        time.sleep(0.3)

        progress.update(task, advance=20, description="⚙️  Configuring project...")

        # Actually generate
        project_path = generator.generate(config)

        progress.update(task, advance=30, description="📦 Setting up dependencies...")
        time.sleep(0.2)

        progress.update(task, advance=20, description="✨ Finalizing...")
        time.sleep(0.2)

        progress.update(task, advance=0, description="✅ Complete!", completed=100)

    return project_path


def show_next_steps(project_path: Path, config: ProjectConfig):
    """Show next steps after generation"""
    steps = f"""
# 🎉 Success! Your project is ready!

## 📍 Location
`{project_path}`

## 🚀 Quick Start

### 1. Navigate to your project
```bash
cd {config.name}
```

### 2. Create virtual environment
```bash
# Linux/macOS
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
source venv\\Scripts\\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment
```bash
cp .env.example .env
# Edit .env with your database credentials
```

### 5. Initialize database
"""

    # Add database-specific commands
    if config.orm == 'SQLAlchemy' and config.framework == 'Flask-Restx':
        steps += """```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```
"""
    elif config.orm == 'SQLAlchemy' and config.framework == 'FastAPI':
        steps += """```bash
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```
"""
    elif config.orm == 'TortoiseORM':
        steps += """```bash
aerich init -t src.config.config.TORTOISE_ORM
aerich init-db
```
"""

    # Add run command
    steps += """
### 6. Run the server
```bash
"""

    if config.framework == 'Flask-Restx':
        steps += "python app.py\n"
    elif config.framework == 'FastAPI':
        steps += "uvicorn src.main:app --reload\n"
    elif config.framework == 'Django-Rest':
        steps += "python manage.py makemigrations\n"
        steps += "python manage.py migrate\n"
        steps += "python manage.py runserver\n"

    steps += "```\n\n"

    # Add documentation URL
    if config.framework == 'Flask-Restx':
        steps += "### 7. Visit API docs\n"
        steps += f"🌐 http://localhost:{config.get_port()}/\n\n"
    elif config.framework == 'FastAPI':
        steps += "### 7. Visit API docs\n"
        steps += f"🌐 http://localhost:{config.get_port()}/docs\n\n"

    # Docker instructions
    if config.docker_support:
        steps += """## 🐳 Docker (Alternative)

```bash
docker-compose up -d
```
"""

    # Testing instructions
    if config.testing_suite:
        steps += """
## 🧪 Running Tests

```bash
pytest
pytest --cov=src --cov-report=html
```
"""

    steps += """
## 📚 Resources

- 📖 Documentation: Check README.md
- 🐛 Issues: Report bugs on GitHub
- 💡 Examples: See examples/ directory

---

**Happy coding! 🎨**
    """

    md = Markdown(steps)
    console.print("\n")
    console.print(Panel(md, border_style="green", padding=(1, 2)))


def show_error(title: str, errors: List[str]):
    """Show error messages"""
    error_text = "\n".join(f"• {error}" for error in errors)

    console.print("\n")
    console.print(Panel(
        f"[bold red]{title}[/bold red]\n\n{error_text}",
        border_style="red",
        padding=(1, 2)
    ))
    console.print("\n")


def show_success(message: str):
    """Show success message"""
    console.print("\n")
    console.print(f"[bold green]✅ {message}[/bold green]")
    console.print("\n")


def show_warning(message: str):
    """Show warning message"""
    console.print("\n")
    console.print(f"[bold yellow]⚠️  {message}[/bold yellow]")
    console.print("\n")