"""
Additional tests for display module
"""

from vyte.cli.display import (
    show_error,
    show_next_steps,
    show_success,
    show_summary,
    show_warning,
    show_welcome,
)
from vyte.core.config import ProjectConfig


def test_show_welcome(capsys):
    """Test welcome message display"""
    show_welcome()
    # Just ensure it doesn't crash
    assert True


def test_show_summary():
    """Test project summary display"""
    config = ProjectConfig(
        name="test-project",
        framework="FastAPI",
        orm="SQLAlchemy",
        database="PostgreSQL",
        auth_enabled=True,
        docker_support=True,
        testing_suite=True,
        git_init=True,
    )

    # Should not raise any exceptions
    show_summary(config)
    assert True


def test_show_next_steps(tmp_path):
    """Test next steps display"""
    config = ProjectConfig(
        name="test-project",
        framework="FastAPI",
        orm="SQLAlchemy",
        database="PostgreSQL",
    )

    project_path = tmp_path / "test-project"
    project_path.mkdir()

    # Should not raise any exceptions
    show_next_steps(project_path, config)
    assert True


def test_show_error():
    """Test error message display"""
    show_error("Test Error", ["Error detail 1", "Error detail 2"])
    assert True


def test_show_success():
    """Test success message display"""
    show_success("Operation completed successfully")
    assert True


def test_show_warning():
    """Test warning message display"""
    show_warning("This is a warning")
    assert True


def test_show_error_with_single_detail():
    """Test error display with single detail"""
    show_error("Single Error", ["Just one detail"])
    assert True


def test_show_error_with_no_details():
    """Test error display with no details"""
    show_error("No Details Error", [])
    assert True


def test_show_next_steps_different_frameworks(tmp_path):
    """Test next steps for different frameworks"""
    frameworks = ["FastAPI", "Flask-Restx", "Django-Rest"]

    for framework in frameworks:
        config = ProjectConfig(
            name=f"test-{framework.lower()}",
            framework=framework,
            orm="SQLAlchemy" if framework != "Django-Rest" else "DjangoORM",
            database="PostgreSQL",
        )

        project_path = tmp_path / config.name
        project_path.mkdir(exist_ok=True)

        # Should not raise any exceptions
        show_next_steps(project_path, config)

    assert True


def test_show_summary_without_optional_features():
    """Test summary display without optional features"""
    config = ProjectConfig(
        name="minimal-project",
        framework="FastAPI",
        orm="SQLAlchemy",
        database="SQLite",
        auth_enabled=False,
        docker_support=False,
        testing_suite=False,
        git_init=False,
    )

    show_summary(config)
    assert True


def test_show_summary_with_all_features():
    """Test summary display with all features enabled"""
    config = ProjectConfig(
        name="full-project",
        framework="FastAPI",
        orm="SQLAlchemy",
        database="PostgreSQL",
        auth_enabled=True,
        docker_support=True,
        testing_suite=True,
        git_init=True,
    )

    show_summary(config)
    assert True
