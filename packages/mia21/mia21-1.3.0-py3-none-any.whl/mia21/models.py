"""Data models for Mia21 SDK."""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union
from enum import Enum


class ChatMessage(BaseModel):
    """A chat message."""
    role: str = Field(..., description="Message role: 'user', 'assistant', 'system', or 'tool'")
    content: Optional[str] = Field(None, description="Message content")
    tool_calls: Optional[List[Dict[str, Any]]] = Field(None, description="Tool calls (for assistant messages)")
    tool_call_id: Optional[str] = Field(None, description="Tool call ID (for tool messages)")


class Space(BaseModel):
    """A space configuration."""
    id: str = Field(..., alias="space_id", description="Space ID")
    name: str = Field(..., description="Space display name")
    description: Optional[str] = Field(None, description="Space description")
    type: Optional[str] = Field(None, description="Space type: 'preset' or 'custom'")
    
    class Config:
        populate_by_name = True  # Allow both 'id' and 'space_id'


class InitializeResponse(BaseModel):
    """Response from initialize_chat."""
    user_id: str
    message: Optional[str] = None
    space_id: Optional[str] = None
    is_new_user: Optional[bool] = None


class ChatResponse(BaseModel):
    """Response from chat."""
    message: str
    user_id: str
    tool_calls: Optional[List[Dict[str, Any]]] = None


class Tool(BaseModel):
    """Tool definition in OpenAI format."""
    type: str = Field(default="function", description="Tool type (always 'function')")
    function: Dict[str, Any] = Field(..., description="Function definition")


class ToolCall(BaseModel):
    """Tool call from LLM."""
    id: str = Field(..., description="Unique tool call ID")
    type: str = Field(default="function", description="Tool type")
    function: Dict[str, Any] = Field(..., description="Function name and arguments")


class StreamEvent(BaseModel):
    """Event from streaming response."""
    type: str = Field(..., description="Event type: text, tool_call, done, error")
    data: Any = Field(..., description="Event data")





