"""
PlimverAI SDK - Python SDK for PlimverAI API

A comprehensive SDK for building AI-powered applications with PlimverAI.
"""

from .zenuxai import (
    PlimverClient,
    AsyncPlimverClient,
    ChatMessage,
    ChatResponse,
    WeatherData,
    UsageStats,
    ModelName,
    RequestType,
    PlimverAPIError,
    AuthenticationError,
    QuotaExceededError,
    RateLimitError,
    create_client,
    create_async_client
)

__version__ = "1.0.0"
__author__ = "PlimverAI Team"
__email__ = "team@plimverai.com"
__license__ = "MIT"

__all__ = [
    'PlimverClient',
    'AsyncPlimverClient',
    'ChatMessage',
    'ChatResponse',
    'WeatherData',
    'UsageStats',
    'ModelName',
    'RequestType',
    'PlimverAPIError',
    'AuthenticationError',
    'QuotaExceededError',
    'RateLimitError',
    'create_client',
    'create_async_client',
    '__version__'
]