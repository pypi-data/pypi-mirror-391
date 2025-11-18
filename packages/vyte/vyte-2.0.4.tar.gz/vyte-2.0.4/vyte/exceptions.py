"""
Custom exceptions for Vyte
"""


class VyteError(Exception):
    """Base exception for all Vyte errors"""


class ConfigurationError(VyteError):
    """Raised when project configuration is invalid"""


class GenerationError(VyteError):
    """Raised when project generation fails"""


class TemplateError(VyteError):
    """Raised when template rendering fails"""


class DependencyError(VyteError):
    """Raised when dependency resolution fails"""


class ValidationError(VyteError):
    """Raised when validation fails"""


class FileSystemError(VyteError):
    """Raised when file system operations fail"""


class GitError(VyteError):
    """Raised when git operations fail"""
