"""
Strategy implementations for different frameworks
"""
from .base import BaseStrategy
from .flask_restx import FlaskRestxStrategy
from .fastapi import FastAPIStrategy
from .django_rest import DjangoRestStrategy

__all__ = [
    'BaseStrategy',
    'FlaskRestxStrategy',
    'FastAPIStrategy',
    'DjangoRestStrategy',
]
