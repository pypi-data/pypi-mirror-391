# src/lingua_agent/llm_api/llm_client.py
import os
from typing import Optional, Dict, Any, List
from openai import OpenAI, AsyncOpenAI
from openai.types.chat import ChatCompletionMessageParam

from .thinking_config import ThinkingConfig


class LLMClient:
    """LLM client that wraps OpenAI API calls and supports chain-of-thought configuration."""

    def __init__(
            self,
            model: str = "deepseek-chat",
            base_url: str = "https://api.deepseek.com/v1  ",
            api_key: Optional[str] = None,
            temperature: float = 0.0,
            max_tokens: Optional[int] = None,
            top_p: float = 1.0,
            timeout: float = 10.0,
            max_retries: int = 3,
            stream: bool = False,
            enable_thinking: bool = False
    ):
        self.model = model
        self.base_url = base_url
        self.api_key = api_key
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.top_p = top_p
        self.timeout = timeout
        self.max_retries = max_retries
        self.stream = stream
        self.enable_thinking = enable_thinking

        # Initialize chain-of-thought configuration
        self.thinking_config = ThinkingConfig()

        # Initialize clients
        self.sync_client = self._setup_sync_client()
        self.async_client = self._setup_async_client()

    @staticmethod
    def _resolve_api_key(api_key: Optional[str] = None) -> Optional[str]:
        """Resolve API key from provided value or environment variables."""
        if api_key:
            return api_key

        env_vars = ["DEEPSEEK_API_KEY", "OPENAI_API_KEY", "ZHIPU_API_KEY", "API_KEY"]
        for env_var in env_vars:
            env_key = os.getenv(env_var)
            if env_key:
                return env_key
        return None

    def _setup_sync_client(self) -> Optional[OpenAI]:
        """Initialize synchronous OpenAI client."""
        resolved_api_key = self._resolve_api_key(self.api_key)
        if not resolved_api_key:
            return None

        client_config = {
            "base_url": self.base_url.strip(),
            "api_key": resolved_api_key,
            "timeout": self.timeout,
            "max_retries": self.max_retries,
        }

        return OpenAI(**client_config)

    def _setup_async_client(self) -> Optional[AsyncOpenAI]:
        """Initialize asynchronous OpenAI client."""
        resolved_api_key = self._resolve_api_key(self.api_key)
        if not resolved_api_key:
            return None

        client_config = {
            "base_url": self.base_url.strip(),
            "api_key": resolved_api_key,
            "timeout": self.timeout,
            "max_retries": self.max_retries,
        }
        return AsyncOpenAI(**client_config)

    def _build_call_params(self, messages: List[ChatCompletionMessageParam], **kwargs) -> Dict[str, Any]:
        """Build API call parameters, including chain-of-thought settings."""
        call_params = {
            "model": kwargs.get("model", self.model),
            "messages": messages,
            "temperature": kwargs.get("temperature", self.temperature),
            "max_tokens": kwargs.get("max_tokens", self.max_tokens),
            "top_p": kwargs.get("top_p", self.top_p),
            "stream": kwargs.get("stream", self.stream),
        }

        # Parameters that can be passed via invoke
        valid_invoke_param_names = {
            "top_logprobs": int,
            "logprobs": bool
        }
        invoke_params = {k: v for k, v in kwargs.items() if k in valid_invoke_param_names and isinstance(v, valid_invoke_param_names[k])}
        call_params.update(invoke_params)

        # Remove None values
        call_params = {k: v for k, v in call_params.items() if v is not None}

        # Add chain-of-thought parameters if enabled
        thinking_params = self.thinking_config.get_thinking_params(
            call_params.get("model"),
            self.enable_thinking
        )
        if thinking_params:
            call_params["extra_body"] = thinking_params

        return call_params

    def call(
            self,
            messages: List[ChatCompletionMessageParam],
            **kwargs
    ) -> Any:
        """Make a synchronous LLM call."""
        if not self.sync_client:
            raise ValueError("Synchronous client is not initialized. Please check your API configuration.")

        call_params = self._build_call_params(messages, **kwargs)

        response = self.sync_client.chat.completions.create(**call_params)
        return response

    async def acall(
            self,
            messages: List[ChatCompletionMessageParam],
            **kwargs
    ) -> Any:
        """Make an asynchronous LLM call."""
        if not self.async_client:
            raise ValueError("Asynchronous client is not initialized. Please check your API configuration.")

        call_params = self._build_call_params(messages, **kwargs)
        response = await self.async_client.chat.completions.create(**call_params)
        return response

    def stream(
            self,
            messages: List[ChatCompletionMessageParam],
            **kwargs
    ):
        """Make a synchronous streaming LLM call."""
        if not self.sync_client:
            raise ValueError("Synchronous client is not initialized. Please check your API configuration.")

        call_params = self._build_call_params(messages, **kwargs)

        call_params["stream"] = True

        response = self.sync_client.chat.completions.create(**call_params)
        return response

    async def astream(
            self,
            messages: List[ChatCompletionMessageParam],
            **kwargs
    ):
        """Make an asynchronous streaming LLM call."""
        if not self.async_client:
            raise ValueError("Asynchronous client is not initialized. Please check your API configuration.")

        call_params = self._build_call_params(messages, **kwargs)
        call_params["stream"] = True

        response = await self.async_client.chat.completions.create(**call_params)
        return response

    def is_configured(self) -> bool:
        """Check if the client is properly configured."""
        return self.sync_client is not None and self.async_client is not None

    def update_config(self, **kwargs):
        """Update client configuration dynamically."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

        # Reinitialize clients if critical parameters changed
        if any(key in kwargs for key in ['api_key', 'base_url', 'timeout', 'max_retries']):
            self.sync_client = self._setup_sync_client()
            self.async_client = self._setup_async_client()

    def enable_thinking_mode(self, enable: bool = True):
        """Enable or disable chain-of-thought reasoning mode."""
        self.enable_thinking = enable

    def get_thinking_status(self) -> Dict[str, Any]:
        """Get the current chain-of-thought mode status."""
        return {
            "enable_thinking": self.enable_thinking,
            "thinking_params": self.thinking_config.get_thinking_params(self.model, self.enable_thinking),
            "model_type": self.thinking_config.get_model_type(self.model)
        }