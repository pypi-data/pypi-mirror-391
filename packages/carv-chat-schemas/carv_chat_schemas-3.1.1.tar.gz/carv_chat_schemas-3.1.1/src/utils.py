# MANUALLY MAINTAINED FILE - DO NOT AUTO-GENERATE
# This file contains utilities for handling StreamEvent discriminated union

from typing import Union, Any
from pydantic import ValidationError

# Import stream event models (these will be available after generation)
try:
    from .messagechunk import MessageChunk
    from .thinkingchunk import ThinkingChunk
    from .toolcallchunk import ToolCallChunk
    from .errorchunk import ErrorChunk
    from .suggestionchunk import SuggestionChunk
except ImportError:
    # Fallback for when models aren't generated yet
    MessageChunk = None
    ThinkingChunk = None
    ToolCallChunk = None
    ErrorChunk = None
    SuggestionChunk = None

# Discriminated union type for all stream events
StreamEvent = Union[MessageChunk, ThinkingChunk, ToolCallChunk, ErrorChunk, SuggestionChunk]


def is_message_chunk(event: Any) -> bool:
    """
    Type guard to check if an event is a MessageChunk.
    
    Args:
        event: The event to check
        
    Returns:
        True if the event is a MessageChunk, False otherwise
    """
    if MessageChunk is None:
        return False
    # Check type field first for performance
    if isinstance(event, dict) and event.get('type') != 'message':
        return False
    try:
        MessageChunk.model_validate(event)
        return True
    except (ValidationError, AttributeError, TypeError):
        return False


def is_thinking_chunk(event: Any) -> bool:
    """
    Type guard to check if an event is a ThinkingChunk.
    
    Args:
        event: The event to check
        
    Returns:
        True if the event is a ThinkingChunk, False otherwise
    """
    if ThinkingChunk is None:
        return False
    # Check type field first for performance
    if isinstance(event, dict) and event.get('type') != 'thinking':
        return False
    try:
        ThinkingChunk.model_validate(event)
        return True
    except (ValidationError, AttributeError, TypeError):
        return False


def is_tool_call_chunk(event: Any) -> bool:
    """
    Type guard to check if an event is a ToolCallChunk.
    
    Args:
        event: The event to check
        
    Returns:
        True if the event is a ToolCallChunk, False otherwise
    """
    if ToolCallChunk is None:
        return False
    # Check type field first for performance
    if isinstance(event, dict) and event.get('type') != 'tool_call':
        return False
    try:
        ToolCallChunk.model_validate(event)
        return True
    except (ValidationError, AttributeError, TypeError):
        return False


def is_error_chunk(event: Any) -> bool:
    """
    Type guard to check if an event is an ErrorChunk.
    
    Args:
        event: The event to check
        
    Returns:
        True if the event is an ErrorChunk, False otherwise
    """
    if ErrorChunk is None:
        return False
    # Check type field first for performance
    if isinstance(event, dict) and event.get('type') != 'error':
        return False
    try:
        ErrorChunk.model_validate(event)
        return True
    except (ValidationError, AttributeError, TypeError):
        return False


def is_suggestion_chunk(event: Any) -> bool:
    """
    Type guard to check if an event is a SuggestionChunk.
    
    Args:
        event: The event to check
        
    Returns:
        True if the event is a SuggestionChunk, False otherwise
    """
    if SuggestionChunk is None:
        return False
    # Check type field first for performance
    if isinstance(event, dict) and event.get('type') != 'suggestion':
        return False
    try:
        SuggestionChunk.model_validate(event)
        return True
    except (ValidationError, AttributeError, TypeError):
        return False


def parse_stream_event(data: Any) -> StreamEvent:
    """
    Parse and validate a stream event using the discriminated union.
    Returns the parsed event with proper type narrowing.
    
    Args:
        data: The raw event data to parse
        
    Returns:
        The parsed StreamEvent
        
    Raises:
        ValueError: If the event does not match any known event type
    """
    # Try each type in order
    if is_message_chunk(data):
        return MessageChunk.model_validate(data)
    if is_thinking_chunk(data):
        return ThinkingChunk.model_validate(data)
    if is_tool_call_chunk(data):
        return ToolCallChunk.model_validate(data)
    if is_error_chunk(data):
        return ErrorChunk.model_validate(data)
    if is_suggestion_chunk(data):
        return SuggestionChunk.model_validate(data)
    
    raise ValueError('Invalid stream event: does not match any known event type')


def safe_parse_stream_event(data: Any) -> dict:
    """
    Safe parse a stream event - returns result instead of throwing.
    
    Args:
        data: The raw event data to parse
        
    Returns:
        A dictionary with 'success' (bool), optional 'data' (StreamEvent), 
        and optional 'error' (Exception)
    """
    try:
        event = parse_stream_event(data)
        return {'success': True, 'data': event}
    except Exception as error:
        return {
            'success': False,
            'error': error if isinstance(error, Exception) else Exception('Unknown error'),
        }

