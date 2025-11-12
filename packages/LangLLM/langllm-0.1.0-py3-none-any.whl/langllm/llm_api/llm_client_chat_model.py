# src/lingua_agent/llm_api/llm_client_chat_model.py
import inspect
from typing import Any, Dict, Iterator, List, Optional, AsyncIterator, cast

from langchain_core.language_models.chat_models import BaseChatModel, _gen_info_and_msg_metadata
from langchain_core.messages import BaseMessage
from langchain_core.messages.utils import convert_to_openai_messages
from langchain_core.messages.ai import _LC_ID_PREFIX
from langchain_core.outputs import ChatResult, ChatGeneration, ChatGenerationChunk
from langchain_core.callbacks import CallbackManagerForLLMRun, AsyncCallbackManagerForLLMRun
from pydantic import Field

from .llm_client import LLMClient
from .message_chunk import ChatMessage, ChatMessageChunk, merge_chunks_to_completion


class LLMClientChatModel(BaseChatModel):
    """Wrap LLMClient as a LangChain ChatModel, supporting custom message types."""
    llm_client: LLMClient = Field(..., description="LLM client instance")

    def __init__(self, llm_client: LLMClient, **kwargs):
        super().__init__(llm_client=llm_client, **kwargs)

    @property
    def _llm_type(self) -> str:
        return "llm_client_chat_model"

    @property
    def _identifying_params(self) -> Dict[str, Any]:
        return {
            "model": self.llm_client.model,
        }

    def _generate(
            self,
            messages: List[BaseMessage],
            stop: Optional[List[str]] = None,
            run_manager: Optional[CallbackManagerForLLMRun] = None,
            **kwargs: Any,
    ) -> ChatResult:
        """Synchronous non-streaming generation."""
        llm_messages = convert_to_openai_messages(messages)

        # Call LLMClient
        response = self.llm_client.call(llm_messages, **kwargs)
        content = response.choices[0].message.content

        # Create appropriate message type
        message = ChatMessage(content=content, chat_completion=response)

        return ChatResult(
            generations=[ChatGeneration(message=message)]
        )

    def _stream(
            self,
            messages: List[BaseMessage],
            stop: Optional[List[str]] = None,
            run_manager: Optional[CallbackManagerForLLMRun] = None,
            **kwargs: Any,
    ) -> Iterator[ChatGenerationChunk]:
        """Synchronous streaming generation - key method."""
        llm_messages = convert_to_openai_messages(messages)

        # Set streaming parameters
        stream_kwargs = {**kwargs, "stream": True}

        # Use LLMClient's streaming call
        for chunk in self.llm_client.stream(llm_messages, **stream_kwargs):
            message = ChatMessageChunk(content="", chat_completion_chunk=chunk)
            generation_chunk = ChatGenerationChunk(message=message)
            # Trigger callback (so astream_events can listen)
            if run_manager:
                run_manager.on_llm_new_token(
                    "",
                    chunk=generation_chunk
                )

            yield generation_chunk

    async def _agenerate(
            self,
            messages: List[BaseMessage],
            stop: Optional[List[str]] = None,
            run_manager: Optional[CallbackManagerForLLMRun] = None,
            **kwargs: Any,
    ) -> ChatResult:
        """Asynchronous non-streaming generation."""
        llm_messages = convert_to_openai_messages(messages)

        # Call LLMClient
        response = await self.llm_client.acall(llm_messages, **kwargs)
        content = response.choices[0].message.content

        # Create appropriate message type
        message = ChatMessage(content=content, chat_completion=response)

        return ChatResult(
            generations=[ChatGeneration(message=message)]
        )

    async def _astream(
            self,
            messages: List[BaseMessage],
            stop: Optional[List[str]] = None,
            run_manager: Optional[CallbackManagerForLLMRun] = None,
            **kwargs: Any,
    ) -> AsyncIterator[ChatGenerationChunk]:
        """Asynchronous streaming generation."""
        llm_messages = convert_to_openai_messages(messages)

        # Set streaming parameters
        stream_kwargs = {**kwargs, "stream": True}

        # Use LLMClient's asynchronous streaming call
        async for chunk in await self.llm_client.astream(llm_messages, **stream_kwargs):
            message = ChatMessageChunk(content="", chat_completion_chunk=chunk)
            generation_chunk = ChatGenerationChunk(message=message)
            # Trigger callback (so astream_events can listen)
            if run_manager:
                run_manager.on_llm_new_token(
                    "",
                    chunk=generation_chunk
                )

            yield generation_chunk

    def _generate_with_cache(
        self,
        messages: list[BaseMessage],
        stop: Optional[list[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """Synchronous generation with caching support."""

        if self._should_stream(
            async_api=False,
            run_manager=run_manager,
            **kwargs,
        ):
            chunks: list[ChatGenerationChunk] = []
            for chunk in self._stream(messages, stop=stop, **kwargs):
                chunk.message.response_metadata = _gen_info_and_msg_metadata(chunk)
                if run_manager:
                    if chunk.message.id is None:
                        chunk.message.id = f"{_LC_ID_PREFIX}-{run_manager.run_id}"
                    run_manager.on_llm_new_token(
                        cast("str", chunk.message.content), chunk=chunk
                    )
                chunks.append(chunk.message.chat_completion_chunk)
            chat_completion = merge_chunks_to_completion(iter(chunks))
            message = ChatMessage(content="", chat_completion=chat_completion)
            result = ChatResult(
                generations=[ChatGeneration(message=message)]
            )

        elif inspect.signature(self._generate).parameters.get("run_manager"):
            result = self._generate(
                messages, stop=stop, run_manager=run_manager, **kwargs
            )
        else:
            result = self._generate(messages, stop=stop, **kwargs)

        return result

    async def _agenerate_with_cache(
        self,
        messages: list[BaseMessage],
        stop: Optional[list[str]] = None,
        run_manager: Optional[AsyncCallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """Asynchronous generation with caching support."""

        # If stream is not explicitly set, check if implicitly requested by
        # astream_events() or astream_log(). Bail out if _astream not implemented
        if self._should_stream(
            async_api=True,
            run_manager=run_manager,
            **kwargs,
        ):
            chunks: list[ChatGenerationChunk] = []
            async for chunk in self._astream(messages, stop=stop, **kwargs):
                chunk.message.response_metadata = _gen_info_and_msg_metadata(chunk)
                if run_manager:
                    if chunk.message.id is None:
                        chunk.message.id = f"{_LC_ID_PREFIX}-{run_manager.run_id}"
                    await run_manager.on_llm_new_token(
                        cast("str", chunk.message.content), chunk=chunk
                    )
                chunks.append(chunk.message.chat_completion_chunk)
            chat_completion = merge_chunks_to_completion(iter(chunks))
            message = ChatMessage(content="", chat_completion=chat_completion)
            result = ChatResult(
                generations=[ChatGeneration(message=message)]
            )
        elif inspect.signature(self._agenerate).parameters.get("run_manager"):
            result = await self._agenerate(
                messages, stop=stop, run_manager=run_manager, **kwargs
            )
        else:
            result = await self._agenerate(messages, stop=stop, **kwargs)

        return result
