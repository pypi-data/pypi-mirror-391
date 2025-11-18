from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel, Field


# Jarvis Step Event Models
class JarvisStepData(BaseModel):
    # Common fields across all step types
    timestamp: Optional[str] = None
    session_id: Optional[str] = None

    # Conversation start
    conversation_id: Optional[str] = None
    user_id: Optional[str] = None

    # Senser phase
    status: Optional[str] = None
    intention: Optional[str] = None
    language: Optional[str] = None
    blocked: Optional[str] = None
    block_reason: Optional[str] = None

    # Thinking
    content: Optional[str] = None

    # Tool execution
    tools: Optional[Dict[str, Any]] = None
    tool_name: Optional[str] = None
    total_tools: Optional[int] = None
    results: Optional[str] = None
    success: Optional[bool] = None
    progress: Optional[str] = None

    # Knowledge search
    queries: Optional[List[str]] = None
    total_queries: Optional[int] = None
    current_query: Optional[str] = None
    doc_links: Optional[List[Dict[str, str]]] = None
    results_summary: Optional[str] = None

    # Document reading
    urls: Optional[List[str]] = None
    total_documents: Optional[int] = None
    reading_goal: Optional[str] = None
    current_url: Optional[str] = None

    # Agent execution
    agent_type: Optional[str] = None
    task: Optional[str] = None
    result: Optional[str] = None

    # Conversation complete
    final_response: Optional[str] = None
    total_time_seconds: Optional[float] = None

    # Error
    error_message: Optional[str] = None
    error_type: Optional[str] = None


class JarvisStep(BaseModel):
    id: Optional[str] = None
    type: str
    node_id: Optional[str] = None
    data: JarvisStepData
    session_id: Optional[str] = None


class JarvisMetadata(BaseModel):
    conversation_id: Optional[str] = None


# Delta models for streaming chunks
class Delta(BaseModel):
    role: Optional[Literal["assistant", "user", "system"]] = None
    content: Optional[str] = None
    jarvis_step: Optional[JarvisStep] = None
    jarvis_metadata: Optional[JarvisMetadata] = None


class Choice(BaseModel):
    index: int
    delta: Optional[Delta] = None
    message: Optional[Dict[str, Any]] = None
    finish_reason: Optional[Literal["stop", "error", None]] = None


class Usage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


# Chat completion response (non-streaming)
class ChatCompletionResponse(BaseModel):
    id: str
    object: Literal["chat.completion"]
    created: int
    model: str
    choices: List[Choice]
    usage: Optional[Usage] = None
    jarvis_metadata: Optional[JarvisMetadata] = None


# Chat completion chunk (streaming)
class ChatCompletionChunk(BaseModel):
    id: str
    object: Literal["chat.completion.chunk"]
    created: int
    model: str
    choices: List[Choice]


# Message model
class Message(BaseModel):
    role: Literal["assistant", "user", "system"]
    content: str


# Jarvis-specific options
class JarvisOptions(BaseModel):
    conversation_id: Optional[str] = None
    mode: Optional[str] = None


# Request models
class ChatCompletionRequest(BaseModel):
    model: str = "jarvis-chat"
    messages: List[Message]
    stream: bool = True
    user: Optional[str] = None
    jarvis_options: Optional[JarvisOptions] = None
