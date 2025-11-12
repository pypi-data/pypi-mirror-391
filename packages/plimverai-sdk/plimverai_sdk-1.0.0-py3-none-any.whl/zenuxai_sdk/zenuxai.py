"""
PlimverAI SDK - Python SDK for PlimverAI API
========================================

A comprehensive Python SDK for interacting with the PlimverAI API system.

Features:
- Chat completions with multiple models
- RAG (Retrieval Augmented Generation)
- Web grounding and search
- Code execution (CodeZ)
- Weather queries
- Memory management
- Usage tracking and analytics
- Async support
- Type hints and proper error handling

Author: PlimverAI Team
Version: 1.0.0
Date: October 2025
"""

import requests
import json
import time
from typing import Dict, List, Optional, Union, Any, AsyncGenerator
from dataclasses import dataclass
from enum import Enum
import asyncio
import aiohttp
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RequestType(Enum):
    """Request types for usage tracking"""
    CHAT = "chat_requests"
    CODE_EXECUTION = "codez_runs"
    MULTIMODAL = "multimodal_requests"
    RAG = "rag_requests"
    GROUNDING = "grounding_searches"
    WEATHER = "weather_requests"
    TOTAL = "total_requests"


class ModelName(Enum):
    """Available PlimverAI models (Production naming)"""
    PLIMVER_TURBO = "PV-TURBO"          # Ultra-fast responses (<1s)
    PLIMVER_STANDARD = "PV-STANDARD"    # Balanced speed & quality
    PLIMVER_ADVANCED = "PV-ADVANCED"    # Deep reasoning & analysis
    PLIMVER_CODEX = "PV-CODEX"          # Code generation & execution

    # Legacy aliases (backward compatibility)
    PLIMVER_1O_FAST = "PV-1o-fast"
    PLIMVER_1O_MID = "PV-1o-mid"
    PLIMVER_1O_HEAVY = "PV-1o-heavy"
    PLIMVER_1O_CODING = "PV-1o-coding"
    PLIMVER_1O_ALPHA = "PV-1o-alpha"       # Alpha maps to turbo


@dataclass
class UsageStats:
    """Usage statistics for API calls"""
    total_requests: int
    chat_requests: int
    rag_requests: int
    grounding_searches: int
    codez_runs: int
    weather_requests: int
    current_period_start: str
    current_period_end: str


@dataclass
class ChatMessage:
    """Chat message structure"""
    role: str  # "user", "assistant", "system"
    content: str

    def to_dict(self) -> Dict[str, str]:
        return {"role": self.role, "content": self.content}


@dataclass
class ChatResponse:
    """Response from chat completion"""
    message: str
    model: str
    provider: str
    tokens_used: int
    weather_tool_used: bool = False
    weather_data: Optional[Dict[str, Any]] = None
    codez_result: Optional[str] = None
    grounding_results: Optional[List[Dict[str, Any]]] = None
    rag_context: Optional[List[Dict[str, Any]]] = None


@dataclass
class WeatherData:
    """Weather information"""
    location: str
    temperature: float
    condition: str
    humidity: int
    wind_speed: float
    timestamp: str


class PlimverAPIError(Exception):
    """Base exception for PlimverAPI errors"""
    pass


class AuthenticationError(PlimverAPIError):
    """Authentication related errors"""
    pass


class QuotaExceededError(PlimverAPIError):
    """Quota limit exceeded"""
    pass


class RateLimitError(PlimverAPIError):
    """Rate limit exceeded"""
    pass


class PlimverClient:
    """
    PlimverAI API Client

    Main client class for interacting with the PlimverAI API.

    Example:
        client = PlimverClient(api_key="your-api-key")
        response = client.chat("Hello, how are you?")
        print(response.message)
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.zenuxai.tech",
        timeout: int = 30,
        max_retries: int = 3,
        retry_delay: float = 1.0
    ):
        """
        Initialize the PlimverAI client.

        Args:
            api_key: Your PlimverAI API key
            base_url: Base URL for the API (default: https://api.zenuxai.tech)
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries for failed requests
            retry_delay: Delay between retries in seconds
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay

        # Set up session with default headers
        self.session = requests.Session()
        self.session.headers.update({
            'X-API-Key': self.api_key,
            'Content-Type': 'application/json',
            'User-Agent': 'PlimverAI-SDK/1.0.0'
        })

    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make HTTP request with error handling and retries.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            data: Request body data
            params: Query parameters

        Returns:
            Response JSON data

        Raises:
            AuthenticationError: Invalid API key
            QuotaExceededError: Usage quota exceeded
            RateLimitError: Rate limit exceeded
            PlimverAPIError: Other API errors
        """
        url = f"{self.base_url}{endpoint}"

        for attempt in range(self.max_retries + 1):
            try:
                if method.upper() == 'GET':
                    response = self.session.get(url, params=params, timeout=self.timeout)
                elif method.upper() == 'POST':
                    response = self.session.post(url, json=data, timeout=self.timeout)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")

                # Handle different response codes
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 401:
                    raise AuthenticationError("Invalid API key")
                elif response.status_code == 403:
                    error_data = response.json()
                    if 'quota' in error_data.get('error', '').lower():
                        raise QuotaExceededError(f"Quota exceeded: {error_data.get('error')}")
                    else:
                        raise AuthenticationError(f"Access denied: {error_data.get('error')}")
                elif response.status_code == 429:
                    raise RateLimitError("Rate limit exceeded")
                else:
                    try:
                        error_data = response.json()
                        raise PlimverAPIError(f"API Error: {error_data.get('error', 'Unknown error')}")
                    except json.JSONDecodeError:
                        raise PlimverAPIError(f"HTTP {response.status_code}: {response.text}")

            except (requests.ConnectionError, requests.Timeout) as e:
                if attempt == self.max_retries:
                    raise PlimverAPIError(f"Request failed after {self.max_retries + 1} attempts: {e}")
                logger.warning(f"Request attempt {attempt + 1} failed, retrying in {self.retry_delay}s...")
                time.sleep(self.retry_delay)

        raise PlimverAPIError("Request failed")

    def chat(
        self,
        message: str,
        user_id: str,
        model: ModelName = ModelName.PLIMVER_1O_FAST,
        use_rag: bool = False,
        rag_k: int = 3,
        use_grounding: bool = False,
        components: Optional[Dict[str, Any]] = None
    ) -> ChatResponse:
        """
        Send a chat message to the AI.

        Args:
            message: The message to send
            user_id: Unique identifier for the user
            model: AI model to use
            use_rag: Whether to use RAG for enhanced responses
            rag_k: Number of documents to retrieve for RAG
            use_grounding: Whether to use web grounding
            components: Additional components configuration

        Returns:
            ChatResponse object with the AI's response

        Example:
            response = client.chat("What's the weather in London?", "user123")
            print(response.message)
        """
        data = {
            "message": message,
            "user_id": user_id,
            "model_name": model.value,
            "use_rag": use_rag,
            "rag_k": rag_k,
            "use_grounding": use_grounding
        }

        if components:
            data["components"] = components

        result = self._make_request('POST', '/api/z1/completions', data)

        # Parse OpenAI-compatible response format
        # API returns: {'choices': [{'message': {'content': '...'}}], 'citations': [...], 'usage': {...}}
        message_content = ''
        if 'choices' in result and len(result['choices']) > 0:
            message_content = result['choices'][0].get('message', {}).get('content', '')
        else:
            # Fallback to legacy format
            message_content = result.get('response', '')

        # Extract tokens from usage object
        tokens = 0
        if 'usage' in result:
            tokens = result['usage'].get('total_tokens', 0)
        else:
            tokens = result.get('tokens_used', 0)

        # Parse weather data if present
        weather_data = None
        if result.get('weather_data'):
            weather_data = WeatherData(**result['weather_data'])

        # Extract citations (OpenAI-compatible format)
        citations = result.get('citations', [])

        return ChatResponse(
            message=message_content,
            model=result.get('model', model.value),
            provider=result.get('provider', 'zenuxai'),
            tokens_used=tokens,
            weather_tool_used=result.get('weather_tool_used', False),
            weather_data=weather_data,
            codez_result=result.get('codez_result'),
            grounding_results=citations if citations else result.get('grounding_results'),
            rag_context=result.get('rag_context')
        )

    def chat_with_history(
        self,
        messages: List[ChatMessage],
        user_id: str,
        model: ModelName = ModelName.PLIMVER_1O_FAST,
        use_rag: bool = False,
        rag_k: int = 3,
        use_grounding: bool = False
    ) -> ChatResponse:
        """
        Send a chat conversation with message history.

        Args:
            messages: List of ChatMessage objects
            user_id: Unique identifier for the user
            model: AI model to use
            use_rag: Whether to use RAG
            rag_k: Number of documents for RAG
            use_grounding: Whether to use web grounding

        Returns:
            ChatResponse object
        """
        # Convert messages to the format expected by the API
        message_list = [msg.to_dict() for msg in messages]

        data = {
            "messages": message_list,
            "user_id": user_id,
            "model_name": model.value,
            "use_rag": use_rag,
            "rag_k": rag_k,
            "use_grounding": use_grounding
        }

        result = self._make_request('POST', '/api/z1/completions', data)

        # Parse OpenAI-compatible response format
        message_content = ''
        if 'choices' in result and len(result['choices']) > 0:
            message_content = result['choices'][0].get('message', {}).get('content', '')
        else:
            message_content = result.get('response', '')

        # Extract tokens from usage object
        tokens = 0
        if 'usage' in result:
            tokens = result['usage'].get('total_tokens', 0)
        else:
            tokens = result.get('tokens_used', 0)

        # Parse weather data if present
        weather_data = None
        if result.get('weather_data'):
            weather_data = WeatherData(**result['weather_data'])

        # Extract citations
        citations = result.get('citations', [])

        return ChatResponse(
            message=message_content,
            model=result.get('model', model.value),
            provider=result.get('provider', 'zenuxai'),
            tokens_used=tokens,
            weather_tool_used=result.get('weather_tool_used', False),
            weather_data=weather_data,
            codez_result=result.get('codez_result'),
            grounding_results=citations if citations else result.get('grounding_results'),
            rag_context=result.get('rag_context')
        )

    def get_weather(self, location: str, user_id: str) -> WeatherData:
        """
        Get weather information for a location.

        Args:
            location: City or location name
            user_id: Unique identifier for the user

        Returns:
            WeatherData object with current weather

        Example:
            weather = client.get_weather("London", "user123")
            print(f"Temperature: {weather.temperature}°C")
        """
        message = f"What's the weather like in {location}?"
        response = self.chat(message, user_id)

        if response.weather_data:
            return response.weather_data
        else:
            raise PlimverAPIError("Weather data not available in response")

    def execute_code(
        self,
        code: str,
        user_id: str,
        language: str = "python"
    ) -> str:
        """
        Execute code using the CodeZ system.

        Args:
            code: Code to execute
            user_id: Unique identifier for the user
            language: Programming language (default: python)

        Returns:
            Execution result as string

        Example:
            result = client.execute_code("print('Hello World')", "user123")
            print(result)
        """
        data = {
            "message": f"Execute this {language} code: {code}",
            "user_id": user_id,
            "components": {
                "codez_needed": True,
                "language": language
            }
        }

        result = self._make_request('POST', '/api/z1/completions', data)
        return result.get('codez_result', 'No execution result')

    def search_web(
        self,
        query: str,
        user_id: str,
        max_results: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Perform web search using grounding.

        Args:
            query: Search query
            user_id: Unique identifier for the user
            max_results: Maximum number of results

        Returns:
            List of search results

        Example:
            results = client.search_web("Python tutorials", "user123")
            for result in results:
                print(result['title'])
        """
        data = {
            "message": query,
            "user_id": user_id,
            "use_grounding": True,
            "grounding_limit": max_results
        }

        result = self._make_request('POST', '/api/z1/completions', data)
        return result.get('grounding_results', [])

    def rag_query(
        self,
        query: str,
        user_id: str,
        k: int = 3
    ) -> Dict[str, Any]:
        """
        Perform RAG query on uploaded documents.

        Args:
            query: Search query
            user_id: Unique identifier for the user
            k: Number of documents to retrieve

        Returns:
            Dictionary with response and context

        Example:
            result = client.rag_query("What are the main features?", "user123")
            print(result['response'])
        """
        data = {
            "message": query,
            "user_id": user_id,
            "use_rag": True,
            "rag_k": k
        }

        result = self._make_request('POST', '/api/z1/completions', data)

        # Parse OpenAI-compatible response format
        message_content = ''
        if 'choices' in result and len(result['choices']) > 0:
            message_content = result['choices'][0].get('message', {}).get('content', '')
        else:
            message_content = result.get('response', '')

        return {
            'response': message_content,
            'context': result.get('rag_context', []),
            'model': result.get('model', ''),
            'tokens_used': result.get('tokens_used', 0)
        }

    def get_usage_stats(self) -> UsageStats:
        """
        Get current usage statistics.

        Returns:
            UsageStats object with current usage information

        Example:
            stats = client.get_usage_stats()
            print(f"Total requests: {stats.total_requests}")
        """
        result = self._make_request('GET', '/dev/usage')

        usage = result.get('usage', {})
        return UsageStats(
            total_requests=usage.get('total_requests', {}).get('current', 0),
            chat_requests=usage.get('chat_requests', {}).get('current', 0),
            rag_requests=usage.get('rag_requests', {}).get('current', 0),
            grounding_searches=usage.get('grounding_searches', {}).get('current', 0),
            codez_runs=usage.get('codez_runs', {}).get('current', 0),
            weather_requests=usage.get('weather_requests', {}).get('current', 0),
            current_period_start=usage.get('current_period_start', ''),
            current_period_end=usage.get('current_period_end', '')
        )

    def upload_file(
        self,
        file_path: str,
        user_id: str,
        file_type: str = "document"
    ) -> Dict[str, Any]:
        """
        Upload a file for processing.

        Args:
            file_path: Path to the file to upload
            user_id: Unique identifier for the user
            file_type: Type of file (document, image, etc.)

        Returns:
            Upload result information

        Note: This method requires the requests library with file upload support.
        """
        with open(file_path, 'rb') as f:
            files = {'file': f}
            data = {'user_id': user_id, 'file_type': file_type}

            # Override content-type for file upload
            headers = self.session.headers.copy()
            del headers['Content-Type']

            response = self.session.post(
                f"{self.base_url}/upload",
                files=files,
                data=data,
                headers=headers,
                timeout=self.timeout
            )

            if response.status_code == 200:
                return response.json()
            else:
                raise PlimverAPIError(f"Upload failed: {response.text}")

    def list_files(self, user_id: str) -> List[Dict[str, Any]]:
        """
        List uploaded files for a user.

        Args:
            user_id: Unique identifier for the user

        Returns:
            List of file information
        """
        params = {"user_id": user_id}
        result = self._make_request('GET', '/files/list', params=params)
        return result.get('files', [])

    def health_check(self) -> Dict[str, Any]:
        """
        Check API health status.

        Returns:
            Dictionary with health status and service information

        Example:
            health = client.health_check()
            print(f"Status: {health['status']}")
            print(f"Services: {health['services']}")
        """
        try:
            result = self._make_request('GET', '/health')
            return result
        except Exception as e:
            return {
                "status": "unreachable",
                "error": str(e)
            }

    def close(self):
        """Close the client session."""
        self.session.close()


class AsyncPlimverClient:
    """
    Asynchronous PlimverAI API Client

    Async version of the PlimverAI client for high-performance applications.

    Example:
        async with AsyncPlimverClient(api_key="your-api-key") as client:
            response = await client.chat("Hello!")
            print(response.message)
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.zenuxai.tech",
        timeout: int = 30,
        max_retries: int = 3,
        retry_delay: float = 1.0
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay

    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            headers={
                'X-API-Key': self.api_key,
                'Content-Type': 'application/json',
                'User-Agent': 'PlimverAI-SDK-Async/1.0.0'
            }
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make async HTTP request with error handling and retries."""
        url = f"{self.base_url}{endpoint}"

        for attempt in range(self.max_retries + 1):
            try:
                async with self.session.request(
                    method,
                    url,
                    json=data,
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:

                    if response.status == 200:
                        return await response.json()
                    elif response.status == 401:
                        raise AuthenticationError("Invalid API key")
                    elif response.status == 403:
                        error_data = await response.json()
                        if 'quota' in error_data.get('error', '').lower():
                            raise QuotaExceededError(f"Quota exceeded: {error_data.get('error')}")
                        else:
                            raise AuthenticationError(f"Access denied: {error_data.get('error')}")
                    elif response.status == 429:
                        raise RateLimitError("Rate limit exceeded")
                    else:
                        try:
                            error_data = await response.json()
                            raise PlimverAPIError(f"API Error: {error_data.get('error', 'Unknown error')}")
                        except:
                            text = await response.text()
                            raise PlimverAPIError(f"HTTP {response.status}: {text}")

            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                if attempt == self.max_retries:
                    raise PlimverAPIError(f"Request failed after {self.max_retries + 1} attempts: {e}")
                logger.warning(f"Request attempt {attempt + 1} failed, retrying in {self.retry_delay}s...")
                await asyncio.sleep(self.retry_delay)

        raise PlimverAPIError("Request failed")

    async def chat(
        self,
        message: str,
        user_id: str,
        model: ModelName = ModelName.PLIMVER_1O_FAST,
        use_rag: bool = False,
        rag_k: int = 3,
        use_grounding: bool = False,
        components: Optional[Dict[str, Any]] = None
    ) -> ChatResponse:
        """Async version of chat method."""
        data = {
            "message": message,
            "user_id": user_id,
            "model_name": model.value,
            "use_rag": use_rag,
            "rag_k": rag_k,
            "use_grounding": use_grounding
        }

        if components:
            data["components"] = components

        result = await self._make_request('POST', '/api/z1/completions', data)

        # Parse OpenAI-compatible response format
        # API returns: {'choices': [{'message': {'content': '...'}}], 'citations': [...], 'usage': {...}}
        message_content = ''
        if 'choices' in result and len(result['choices']) > 0:
            message_content = result['choices'][0].get('message', {}).get('content', '')
        else:
            # Fallback to legacy format
            message_content = result.get('response', '')

        # Extract tokens from usage object
        tokens = 0
        if 'usage' in result:
            tokens = result['usage'].get('total_tokens', 0)
        else:
            tokens = result.get('tokens_used', 0)

        # Parse weather data if present
        weather_data = None
        if result.get('weather_data'):
            weather_data = WeatherData(**result['weather_data'])

        # Extract citations (OpenAI-compatible format)
        citations = result.get('citations', [])

        return ChatResponse(
            message=message_content,
            model=result.get('model', model.value),
            provider=result.get('provider', 'zenuxai'),
            tokens_used=tokens,
            weather_tool_used=result.get('weather_tool_used', False),
            weather_data=weather_data,
            codez_result=result.get('codez_result'),
            grounding_results=citations if citations else result.get('grounding_results'),
            rag_context=result.get('rag_context')
        )

    async def get_weather(self, location: str, user_id: str) -> WeatherData:
        """Async version of get_weather method."""
        message = f"What's the weather like in {location}?"
        response = await self.chat(message, user_id)

        if response.weather_data:
            return response.weather_data
        else:
            raise PlimverAPIError("Weather data not available in response")

    async def execute_code(self, code: str, user_id: str, language: str = "python") -> str:
        """Async version of execute_code method."""
        data = {
            "message": f"Execute this {language} code: {code}",
            "user_id": user_id,
            "components": {
                "codez_needed": True,
                "language": language
            }
        }

        result = await self._make_request('POST', '/api/z1/completions', data)
        return result.get('codez_result', 'No execution result')

    async def search_web(self, query: str, user_id: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Async version of search_web method."""
        data = {
            "message": query,
            "user_id": user_id,
            "use_grounding": True,
            "grounding_limit": max_results
        }

        result = await self._make_request('POST', '/api/z1/completions', data)
        return result.get('grounding_results', [])

    async def rag_query(self, query: str, user_id: str, k: int = 3) -> Dict[str, Any]:
        """Async version of rag_query method."""
        data = {
            "message": query,
            "user_id": user_id,
            "use_rag": True,
            "rag_k": k
        }

        result = await self._make_request('POST', '/api/z1/completions', data)

        # Parse OpenAI-compatible response format
        message_content = ''
        if 'choices' in result and len(result['choices']) > 0:
            message_content = result['choices'][0].get('message', {}).get('content', '')
        else:
            message_content = result.get('response', '')

        return {
            'response': message_content,
            'context': result.get('rag_context', []),
            'model': result.get('model', ''),
            'tokens_used': result.get('tokens_used', 0)
        }

    async def get_usage_stats(self) -> UsageStats:
        """Async version of get_usage_stats method."""
        result = await self._make_request('GET', '/dev/usage')

        usage = result.get('usage', {})
        return UsageStats(
            total_requests=usage.get('total_requests', {}).get('current', 0),
            chat_requests=usage.get('chat_requests', {}).get('current', 0),
            rag_requests=usage.get('rag_requests', {}).get('current', 0),
            grounding_searches=usage.get('grounding_searches', {}).get('current', 0),
            codez_runs=usage.get('codez_runs', {}).get('current', 0),
            weather_requests=usage.get('weather_requests', {}).get('current', 0),
            current_period_start=usage.get('current_period_start', ''),
            current_period_end=usage.get('current_period_end', '')
        )


# Convenience functions for quick usage
def create_client(api_key: str, **kwargs) -> PlimverClient:
    """Create a PlimverAI client instance."""
    return PlimverClient(api_key, **kwargs)


def create_async_client(api_key: str, **kwargs) -> AsyncPlimverClient:
    """Create an async PlimverAI client instance."""
    return AsyncPlimverClient(api_key, **kwargs)


# Export main classes and functions
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
    'create_async_client'
]