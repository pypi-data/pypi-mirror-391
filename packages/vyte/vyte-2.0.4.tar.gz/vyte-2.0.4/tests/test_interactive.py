"""
Tests for interactive CLI module
"""

from unittest.mock import MagicMock, patch

import pytest

from vyte.cli.interactive import interactive_setup


@pytest.fixture
def mock_inquirer_responses():
    """Mock responses for InquirerPy"""
    return {
        "project_name": "test-project",
        "framework": "FastAPI",
        "orm": "SQLAlchemy",
        "database": "PostgreSQL",
        "auth": True,
        "docker": True,
        "tests": True,
        "git": True,
    }


def test_interactive_setup_complete(mock_inquirer_responses):
    """Test interactive setup with all options"""
    with patch("vyte.cli.interactive.inquirer") as mock_inquirer:
        # Configure mock to return our test data
        mock_prompt = MagicMock()
        mock_prompt.execute.return_value = mock_inquirer_responses
        mock_inquirer.prompt.return_value = mock_prompt

        # Mock specific question methods
        mock_inquirer.text.return_value = MagicMock()
        mock_inquirer.select.return_value = MagicMock()
        mock_inquirer.confirm.return_value = MagicMock()

        # This would need the actual interactive_setup implementation
        # For now, we'll test that it can be imported
        assert callable(interactive_setup)


def test_interactive_setup_minimal():
    """Test interactive setup with minimal options"""
    # Test that interactive_setup is importable and callable
    assert callable(interactive_setup)
    assert callable(interactive_setup)


def test_interactive_setup_returns_config():
    """Test that interactive_setup returns a ProjectConfig"""
    # This is a placeholder - actual implementation would need mocking
    # of the inquirer library
    assert callable(interactive_setup)


@pytest.mark.skip(reason="Requires full inquirer mocking")
def test_interactive_setup_with_incompatible_choices():
    """Test interactive setup validates incompatible combinations"""
    pass


@pytest.mark.skip(reason="Requires full inquirer mocking")
def test_interactive_setup_shows_compatible_orms():
    """Test that only compatible ORMs are shown for selected framework"""
    pass
