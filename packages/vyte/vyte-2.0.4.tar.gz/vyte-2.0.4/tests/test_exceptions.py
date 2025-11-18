"""
Tests for custom exceptions
"""

import pytest

from vyte.exceptions import (
    ConfigurationError,
    DependencyError,
    FileSystemError,
    GenerationError,
    GitError,
    TemplateError,
    ValidationError,
    VyteError,
)


def test_vyte_error_base():
    """Test base VyteError exception"""
    with pytest.raises(VyteError):
        raise VyteError("Base error")


def test_configuration_error():
    """Test ConfigurationError exception"""
    with pytest.raises(ConfigurationError):
        raise ConfigurationError("Invalid configuration")

    # Should be catchable as VyteError
    with pytest.raises(VyteError):
        raise ConfigurationError("Invalid configuration")


def test_generation_error():
    """Test GenerationError exception"""
    with pytest.raises(GenerationError):
        raise GenerationError("Generation failed")

    with pytest.raises(VyteError):
        raise GenerationError("Generation failed")


def test_template_error():
    """Test TemplateError exception"""
    with pytest.raises(TemplateError):
        raise TemplateError("Template not found")


def test_dependency_error():
    """Test DependencyError exception"""
    with pytest.raises(DependencyError):
        raise DependencyError("Dependency conflict")


def test_validation_error():
    """Test ValidationError exception"""
    with pytest.raises(ValidationError):
        raise ValidationError("Validation failed")


def test_filesystem_error():
    """Test FileSystemError exception"""
    with pytest.raises(FileSystemError):
        raise FileSystemError("Permission denied")


def test_git_error():
    """Test GitError exception"""
    with pytest.raises(GitError):
        raise GitError("Git command failed")


def test_exception_messages():
    """Test that exception messages are preserved"""
    message = "Test error message"

    try:
        raise ConfigurationError(message)
    except ConfigurationError as e:
        assert str(e) == message

    try:
        raise GenerationError(message)
    except GenerationError as e:
        assert str(e) == message


def test_exception_chaining():
    """Test exception chaining with from"""
    original = ValueError("Original error")

    try:
        try:
            raise original
        except ValueError as e:
            raise GenerationError("Generation failed") from e
    except GenerationError as e:
        assert e.__cause__ == original
        assert str(e) == "Generation failed"
