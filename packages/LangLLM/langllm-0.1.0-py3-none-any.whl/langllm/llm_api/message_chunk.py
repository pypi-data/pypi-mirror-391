# src/lingua_agent/llm_api/message_chunk.py
import time
from typing import Iterator, Optional

from openai.types.chat.chat_completion import ChatCompletion
from openai.types.chat.chat_completion_chunk import ChatCompletionChunk
from openai.types.chat import ChatCompletionMessage
from openai.types.completion_usage import CompletionUsage
from langchain_core.messages import BaseMessage, BaseMessageChunk


class ChatMessage(BaseMessage):
    """A message wrapper that includes the full ChatCompletion response."""
    chat_completion: Optional[ChatCompletion] = None
    type: str = "chat_completion"
    
    @classmethod  
    def get_lc_namespace(cls) -> list[str]:
        return ["langchain", "schema", "messages"]
    

class ChatMessageChunk(BaseMessageChunk):
    """A message chunk wrapper that includes a ChatCompletionChunk."""
    chat_completion_chunk: Optional[ChatCompletionChunk] = None
    type: str = "chat_completion_chunk"
    
    @classmethod  
    def get_lc_namespace(cls) -> list[str]:
        return ["langchain", "schema", "messages"]


def merge_chunks_to_completion(chunks: Iterator[ChatCompletionChunk]) -> ChatCompletion:
    """
    Merge a stream of ChatCompletionChunks into a single ChatCompletion object,
    with support for reasoning/thinking content.

    Args:
        chunks: An iterator of ChatCompletionChunk objects.
        
    Returns:
        A merged ChatCompletion object.
    """
    from typing import Dict, Any
    
    # Initialize merged fields
    merged_id = None
    merged_created = None
    merged_model = None
    merged_choices = []
    merged_usage = None
    merged_system_fingerprint = None
    
    # Track the merged state for each choice by index
    choice_states: Dict[int, Dict[str, Any]] = {}
    
    for chunk in chunks:
        # Populate top-level fields using the first non-null values
        if merged_id is None and chunk.id:
            merged_id = chunk.id
        if merged_created is None and chunk.created:
            merged_created = chunk.created
        if merged_model is None and chunk.model:
            merged_model = chunk.model
        if merged_system_fingerprint is None and chunk.system_fingerprint:
            merged_system_fingerprint = chunk.system_fingerprint
        
        # Accumulate usage statistics
        if chunk.usage:
            if merged_usage is None:
                merged_usage = CompletionUsage(
                    prompt_tokens=chunk.usage.prompt_tokens or 0,
                    completion_tokens=chunk.usage.completion_tokens or 0,
                    total_tokens=chunk.usage.total_tokens or 0
                )
            else:
                merged_usage.prompt_tokens = (merged_usage.prompt_tokens or 0) + (chunk.usage.prompt_tokens or 0)
                merged_usage.completion_tokens = (merged_usage.completion_tokens or 0) + (chunk.usage.completion_tokens or 0)
                merged_usage.total_tokens = (merged_usage.total_tokens or 0) + (chunk.usage.total_tokens or 0)
        
        # Process choices
        for choice in chunk.choices:
            choice_index = choice.index
            
            if choice_index not in choice_states:
                # Initialize state for this choice
                choice_states[choice_index] = {
                    'message': ChatCompletionMessage(role="assistant", content=""),
                    'finish_reason': None,
                    'logprobs': None,
                    'reasoning_content': ""  # Dedicated field for reasoning/thinking content
                }
            
            state = choice_states[choice_index]
            
            # Merge delta content
            delta = choice.delta
            if delta:
                # Handle role
                if delta.role and not state['message'].role:
                    state['message'].role = delta.role
                
                # Handle regular content (final response)
                if delta.content:
                    state['message'].content = (state['message'].content or "") + delta.content
                
                # Handle reasoning/thinking content
                if hasattr(delta, 'reasoning_content') and delta.reasoning_content:
                    state['reasoning_content'] = (state['reasoning_content'] or "") + delta.reasoning_content
            
            # Update finish reason
            if choice.finish_reason:
                state['finish_reason'] = choice.finish_reason
            
            # Handle logprobs correctly
            if choice.logprobs:
                # Convert logprobs to dictionary if it's a Pydantic model
                if hasattr(choice.logprobs, 'model_dump'):
                    state['logprobs'] = choice.logprobs.model_dump()
                elif hasattr(choice.logprobs, 'dict'):
                    state['logprobs'] = choice.logprobs.dict()
                else:
                    # Assume it's already a dictionary
                    state['logprobs'] = choice.logprobs
    
    # Build the final choices list
    for index in sorted(choice_states.keys()):
        state = choice_states[index]
        
        # Construct the choice dictionary
        choice_dict = {
            'index': index,
            'message': state['message'],
            'finish_reason': state['finish_reason'],
            'logprobs': state['logprobs']  # Already in dict format
        }
        
        # If reasoning content exists, embed it in the message as a custom field
        if state['reasoning_content']:
            message_dict = state['message'].model_dump()
            message_dict['reasoning_content'] = state['reasoning_content']
            choice_dict['message'] = message_dict
        
        merged_choices.append(choice_dict)
    
    # Set defaults if fields were never populated
    if merged_id is None:
        merged_id = f"chatcmpl-{int(time.time())}"
    if merged_created is None:
        merged_created = int(time.time())
    if merged_model is None:
        merged_model = "default"
    
    # Create and return the final ChatCompletion object
    return ChatCompletion(
        id=merged_id,
        choices=merged_choices,
        created=merged_created,
        model=merged_model,
        object="chat.completion",
        usage=merged_usage,
        system_fingerprint=merged_system_fingerprint
    )