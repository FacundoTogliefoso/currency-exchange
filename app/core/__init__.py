# app/core/__init__.py
"""
Core module for application configuration and utilities.

This module provides:
- Application configuration and settings management
- Redis client for caching operations
- Circuit breaker pattern for fault tolerance
"""

from .circuit_breaker import CircuitBreaker, CircuitState
from .config import settings
from .redis import redis_client

__all__ = [
    "settings",
    "redis_client",
    "CircuitBreaker",
    "CircuitState",
]
