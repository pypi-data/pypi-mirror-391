import asyncio
import contextvars
from typing import Union

from pydantic import ConfigDict, validate_call
from strands import Agent
from strands.models import Model
from strands.types.tools import AgentTool


def _in_asyncio_context() -> bool:
    try:
        asyncio.get_running_loop()
        return True
    except RuntimeError:
        return False


def _get_or_create_context_var(
    obj: object, async_attr_name: str, default_value: Union[dict, str]
) -> contextvars.ContextVar:
    """Get or create a ContextVar for async attribute storage."""
    if not hasattr(obj, async_attr_name):
        setattr(
            obj,
            async_attr_name,
            contextvars.ContextVar(async_attr_name, default=default_value),
        )
    return getattr(obj, async_attr_name)


def _set_dict_attribute_async(
    obj: object, async_attr_name: str, **kwargs: Union[str, int, float, bool]
) -> None:
    """Set dictionary attributes in async context."""
    context_var = _get_or_create_context_var(obj, async_attr_name, {})
    updated_attributes = context_var.get().copy()
    updated_attributes.update(kwargs)
    context_var.set(updated_attributes)


def _set_dict_attribute_sync(
    obj: object, sync_attr_name: str, **kwargs: Union[str, int, float, bool]
) -> None:
    """Set dictionary attributes in sync context."""
    if not hasattr(obj, sync_attr_name):
        setattr(obj, sync_attr_name, {})
    getattr(obj, sync_attr_name).update(kwargs)


def _get_dict_attribute_async(
    obj: object, async_attr_name: str
) -> dict[str, Union[str, int, float, bool]]:
    """Get dictionary attributes from async context."""
    if hasattr(obj, async_attr_name):
        try:
            return getattr(obj, async_attr_name).get().copy()
        except LookupError:
            pass
    return {}


def _get_dict_attribute_sync(
    obj: object, sync_attr_name: str
) -> dict[str, Union[str, int, float, bool]]:
    """Get dictionary attributes from sync context."""
    if hasattr(obj, sync_attr_name):
        return getattr(obj, sync_attr_name).copy()
    return {}


def _set_string_attribute_async(obj: object, async_attr_name: str, value: str) -> None:
    """Set string attribute in async context."""
    context_var = _get_or_create_context_var(obj, async_attr_name, '')
    context_var.set(value)


def _set_string_attribute_sync(obj: object, sync_attr_name: str, value: str) -> None:
    """Set string attribute in sync context."""
    setattr(obj, sync_attr_name, value)


def _get_string_attribute_async(obj: object, async_attr_name: str) -> str:
    """Get string attribute from async context."""
    if hasattr(obj, async_attr_name):
        try:
            return getattr(obj, async_attr_name).get()
        except LookupError:
            pass
    return ''


def _get_string_attribute_sync(obj: object, sync_attr_name: str) -> str:
    """Get string attribute from sync context."""
    if hasattr(obj, sync_attr_name):
        return getattr(obj, sync_attr_name)
    return ''


@validate_call(config=ConfigDict(strict=True, arbitrary_types_allowed=True))
def set_span_attributes(
    obj: Union[Model, AgentTool], **kwargs: Union[str, int, float, bool]
) -> None:
    """
    Set a custom attribute on an Model & AgentTool that can be accessed by logging hooks.

    This function stores key-value pairs as attributes on the object, making
    them accessible to hooks during model invocation events.

    Args:
        obj: The object to set the attribute on (typically a model or tool)
        **kwargs: Key-value pairs of attributes to set
    """
    if _in_asyncio_context():
        _set_dict_attribute_async(obj, '_async_fiddler_span_attributes', **kwargs)
    else:
        _set_dict_attribute_sync(obj, '_sync_fiddler_span_attributes', **kwargs)


@validate_call(config=ConfigDict(strict=True, arbitrary_types_allowed=True))
def get_span_attributes(
    obj: Union[Model, AgentTool],
) -> dict[str, Union[str, int, float, bool]]:
    """
    Get span attributes from an object.
    Returns an empty dictionary if the object has no attributes.
    """
    if _in_asyncio_context() and hasattr(obj, '_async_fiddler_span_attributes'):
        return _get_dict_attribute_async(obj, '_async_fiddler_span_attributes')
    return _get_dict_attribute_sync(obj, '_sync_fiddler_span_attributes')


@validate_call(config=ConfigDict(strict=True, arbitrary_types_allowed=True))
def set_conversation_id(agent: Agent, conversation_id: str) -> None:
    """Set the conversation ID for the current application invocation.
    This will remain in use until it is called again with a new conversation ID.
    """
    if _in_asyncio_context():
        _set_string_attribute_async(
            agent, '_async_fiddler_conversation_id', conversation_id
        )
    else:
        _set_string_attribute_sync(
            agent, '_sync_fiddler_conversation_id', conversation_id
        )


@validate_call(config=ConfigDict(strict=True, arbitrary_types_allowed=True))
def get_conversation_id(agent: Agent) -> str:
    """Get the conversation ID for the current application invocation.
    This will remain in use until it is called again with a new conversation ID.
    """
    if _in_asyncio_context() and hasattr(agent, '_async_fiddler_conversation_id'):
        return _get_string_attribute_async(agent, '_async_fiddler_conversation_id')
    return _get_string_attribute_sync(agent, '_sync_fiddler_conversation_id')


@validate_call(config=ConfigDict(strict=True, arbitrary_types_allowed=True))
def set_session_attributes(
    agent: Agent, **kwargs: Union[str, int, float, bool]
) -> None:
    """Adds Fiddler-specific attributes to a runnable's metadata."""
    if _in_asyncio_context():
        _set_dict_attribute_async(agent, '_async_fiddler_session_attributes', **kwargs)
    else:
        _set_dict_attribute_sync(agent, '_sync_fiddler_session_attributes', **kwargs)


@validate_call(config=ConfigDict(strict=True, arbitrary_types_allowed=True))
def get_session_attributes(
    agent: Agent,
) -> dict[str, Union[str, int, float, bool]]:
    """Get the session attributes for the current application invocation."""
    if _in_asyncio_context() and hasattr(agent, '_async_fiddler_session_attributes'):
        return _get_dict_attribute_async(agent, '_async_fiddler_session_attributes')
    return _get_dict_attribute_sync(agent, '_sync_fiddler_session_attributes')


@validate_call(config=ConfigDict(strict=True, arbitrary_types_allowed=True))
def set_llm_context(model: Model, context: str) -> None:
    """Set the LLM context for the current application invocation."""
    if _in_asyncio_context():
        _set_string_attribute_async(model, '_async_fiddler_llm_context', context)
    else:
        _set_string_attribute_sync(model, '_sync_fiddler_llm_context', context)


@validate_call(config=ConfigDict(strict=True, arbitrary_types_allowed=True))
def get_llm_context(model: Model) -> str:
    """Get the LLM context for the current application invocation."""
    if _in_asyncio_context() and hasattr(model, '_async_fiddler_llm_context'):
        return _get_string_attribute_async(model, '_async_fiddler_llm_context')
    return _get_string_attribute_sync(model, '_sync_fiddler_llm_context')
