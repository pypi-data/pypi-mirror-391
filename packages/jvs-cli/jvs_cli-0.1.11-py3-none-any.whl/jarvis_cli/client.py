import httpx
import orjson
import time
import re
from typing import AsyncIterator, List, Optional, Dict, Any
from abc import ABC, abstractmethod
from .models import (
    ChatCompletionRequest,
    ChatCompletionChunk,
    Message,
    Delta,
    Choice,
    JarvisOptions,
)
from .config import APIProvider
from .logger import get_debug_logger


class BaseAPIClient(ABC):
    """Base class for API clients"""

    def __init__(self, timeout: float = 120.0):
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=timeout)
        self.debug_logger = get_debug_logger()

    async def close(self) -> None:
        await self.client.aclose()

    @abstractmethod
    async def chat_completion_stream(
        self,
        messages: List[Message],
        conversation_id: Optional[str] = None,
    ) -> AsyncIterator[ChatCompletionChunk]:
        pass


def extract_doc_id_from_url(url: str) -> Optional[str]:
    """Extract document ID from Lark doc URL"""
    match = re.search(r'/docx/([a-zA-Z0-9]+)', url)
    if match:
        return match.group(1)
    return None


async def fetch_lark_document(doc_id: str) -> Dict[str, Any]:
    """Fetch Lark document content from API"""
    url = f"https://page.atomecorp.net/doc-api/jvs/doc/get/{doc_id}"

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()

            if data.get("code") == 0:
                return data.get("data", {})
            else:
                raise RuntimeError(f"API error: {data.get('message', 'Unknown error')}")
        except httpx.HTTPStatusError as e:
            raise RuntimeError(f"Failed to fetch document: HTTP {e.response.status_code}")
        except Exception as e:
            raise RuntimeError(f"Failed to fetch document: {e}")


class JarvisAPIClient(BaseAPIClient):
    """Jarvis backend API client"""

    def __init__(
        self,
        base_url: str,
        user_id: str,
        timeout: float = 120.0,
        jwt_token: Optional[str] = None,
        token_expires_at: Optional[str] = None,
        on_token_refresh: Optional[callable] = None,
    ):
        super().__init__(timeout)
        self.base_url = base_url.rstrip("/")
        self.user_id = user_id
        self.jwt_token = jwt_token
        self.token_expires_at = token_expires_at
        self.on_token_refresh = on_token_refresh

    async def _ensure_valid_token(self) -> None:
        """Ensure JWT token is valid, trigger re-login if expired"""
        if not self.jwt_token:
            return

        from .login import is_token_valid, login
        from rich.console import Console

        if not is_token_valid(self.token_expires_at):
            console = Console()
            console.print("\n[yellow]Token expired. Re-authenticating...[/yellow]")

            try:
                new_token, expires_at = await login(console=console)
                self.jwt_token = new_token
                self.token_expires_at = expires_at.isoformat()

                if self.on_token_refresh:
                    self.on_token_refresh(new_token, expires_at.isoformat())

                console.print("[green]✓[/green] Re-authentication successful\n")
            except Exception as e:
                raise RuntimeError(f"Re-authentication failed: {e}")

    def _build_headers(self) -> Dict[str, str]:
        """Build request headers with authentication"""
        headers = {"Content-Type": "application/json"}

        if self.jwt_token:
            headers["Authorization"] = f"Bearer {self.jwt_token}"

        return headers

    async def chat_completion_stream(
        self,
        messages: List[Message],
        conversation_id: Optional[str] = None,
        mode: Optional[str] = None,
    ) -> AsyncIterator[ChatCompletionChunk]:
        await self._ensure_valid_token()

        jarvis_options = None
        if conversation_id:
            jarvis_options = JarvisOptions(conversation_id=conversation_id, mode=mode)
        else:
            jarvis_options = JarvisOptions(conversation_id="", mode=mode)

        request = ChatCompletionRequest(
            model="jarvis-chat",
            messages=messages,
            stream=True,
            user=self.user_id,
            jarvis_options=jarvis_options,
        )

        url = f"{self.base_url}/chat/completions"

        self.debug_logger.log_request({
            "provider": "jarvis",
            "url": url,
            "messages": [m.model_dump() for m in messages],
            "conversation_id": conversation_id,
            "jarvis_options": jarvis_options.model_dump() if jarvis_options else None,
            "stream": True,
            "auth_method": "bearer_token" if self.jwt_token else "user_field"
        })

        try:
            async with self.client.stream(
                "POST",
                url,
                json=request.model_dump(),
                headers=self._build_headers(),
            ) as response:
                response.raise_for_status()
                async for chunk in self._parse_sse_stream(response):
                    yield chunk
        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP error {e.response.status_code}: {e.response.text}"
            self.debug_logger.log_error(error_msg)
            raise RuntimeError(error_msg)
        except Exception as e:
            error_msg = f"Failed to stream chat completion: {e}"
            self.debug_logger.log_error(error_msg)
            raise RuntimeError(error_msg)

    async def _parse_sse_stream(
        self, response: httpx.Response
    ) -> AsyncIterator[ChatCompletionChunk]:
        async for line_bytes in response.aiter_lines():
            line = line_bytes.strip()
            if not line:
                continue
            if line == "data: [DONE]":
                break
            if line.startswith("data: "):
                data_str = line[6:]
                try:
                    data = orjson.loads(data_str)
                    self.debug_logger.log_chunk(data)
                    chunk = ChatCompletionChunk(**data)
                    yield chunk
                except (orjson.JSONDecodeError, Exception):
                    continue


class OpenAIClient(BaseAPIClient):
    """OpenAI API client"""

    def __init__(self, api_key: str, model: str = "gpt-4-turbo", timeout: float = 120.0):
        super().__init__(timeout)
        self.api_key = api_key
        self.model = model
        self.base_url = "https://api.openai.com/v1"

    async def chat_completion_stream(
        self,
        messages: List[Message],
        conversation_id: Optional[str] = None,
    ) -> AsyncIterator[ChatCompletionChunk]:
        request_data = {
            "model": self.model,
            "messages": [m.model_dump() for m in messages],
            "stream": True,
        }

        url = f"{self.base_url}/chat/completions"

        self.debug_logger.log_request({
            "provider": "openai",
            "url": url,
            "model": self.model,
            "messages": [m.model_dump() for m in messages],
        })

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        try:
            async with self.client.stream(
                "POST",
                url,
                json=request_data,
                headers=headers,
            ) as response:
                response.raise_for_status()
                async for chunk in self._parse_openai_stream(response):
                    yield chunk
        except httpx.HTTPStatusError as e:
            error_msg = f"OpenAI HTTP error {e.response.status_code}: {e.response.text}"
            self.debug_logger.log_error(error_msg)
            raise RuntimeError(error_msg)
        except Exception as e:
            error_msg = f"Failed to stream from OpenAI: {e}"
            self.debug_logger.log_error(error_msg)
            raise RuntimeError(error_msg)

    async def _parse_openai_stream(
        self, response: httpx.Response
    ) -> AsyncIterator[ChatCompletionChunk]:
        async for line_bytes in response.aiter_lines():
            line = line_bytes.strip()
            if not line:
                continue
            if line == "data: [DONE]":
                break
            if line.startswith("data: "):
                data_str = line[6:]
                try:
                    data = orjson.loads(data_str)
                    self.debug_logger.log_chunk(data)

                    # Convert OpenAI format to our format
                    chunk = self._convert_openai_chunk(data)
                    if chunk:
                        yield chunk
                except (orjson.JSONDecodeError, Exception) as e:
                    self.debug_logger.log_error(f"Failed to parse chunk: {e}")
                    continue

    def _convert_openai_chunk(self, data: Dict[str, Any]) -> Optional[ChatCompletionChunk]:
        """Convert OpenAI chunk format to our internal format"""
        if not data.get("choices"):
            return None

        # Create a ChatCompletionChunk from OpenAI data
        choices = []
        for choice_data in data["choices"]:
            delta_data = choice_data.get("delta", {})
            delta = Delta(
                role=delta_data.get("role"),
                content=delta_data.get("content"),
            )
            choice = Choice(
                index=choice_data["index"],
                delta=delta,
                finish_reason=choice_data.get("finish_reason"),
            )
            choices.append(choice)

        return ChatCompletionChunk(
            id=data["id"],
            object=data["object"],
            created=data["created"],
            model=data["model"],
            choices=choices,
        )


class ClaudeClient(BaseAPIClient):
    """Anthropic Claude API client"""

    def __init__(self, api_key: str, model: str = "claude-haiku-4-5-20251001", timeout: float = 120.0):
        super().__init__(timeout)
        self.api_key = api_key
        self.model = model
        self.base_url = "https://api.anthropic.com/v1"

    async def chat_completion_stream(
        self,
        messages: List[Message],
        conversation_id: Optional[str] = None,
    ) -> AsyncIterator[ChatCompletionChunk]:
        # Convert messages to Claude format
        claude_messages = self._convert_messages_to_claude(messages)

        request_data = {
            "model": self.model,
            "messages": claude_messages,
            "stream": True,
            "max_tokens": 4096,
        }

        url = f"{self.base_url}/messages"

        self.debug_logger.log_request({
            "provider": "claude",
            "url": url,
            "model": self.model,
            "messages": claude_messages,
        })

        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        }

        try:
            async with self.client.stream(
                "POST",
                url,
                json=request_data,
                headers=headers,
            ) as response:
                response.raise_for_status()
                async for chunk in self._parse_claude_stream(response):
                    yield chunk
        except httpx.HTTPStatusError as e:
            error_msg = f"Claude HTTP error {e.response.status_code}: {e.response.text}"
            self.debug_logger.log_error(error_msg)
            raise RuntimeError(error_msg)
        except Exception as e:
            error_msg = f"Failed to stream from Claude: {e}"
            self.debug_logger.log_error(error_msg)
            raise RuntimeError(error_msg)

    def _convert_messages_to_claude(self, messages: List[Message]) -> List[Dict[str, str]]:
        """Convert our message format to Claude's format"""
        claude_messages = []
        for msg in messages:
            # Claude doesn't use system role in messages, handle it separately
            if msg.role == "system":
                # System messages should be handled differently in Claude
                # For now, convert to user message with a note
                claude_messages.append({
                    "role": "user",
                    "content": f"[System]: {msg.content}"
                })
            else:
                claude_messages.append({
                    "role": msg.role,
                    "content": msg.content,
                })
        return claude_messages

    async def _parse_claude_stream(
        self, response: httpx.Response
    ) -> AsyncIterator[ChatCompletionChunk]:
        import time
        message_id = f"claude-{int(time.time())}"
        chunk_index = 0

        async for line_bytes in response.aiter_lines():
            line = line_bytes.strip()
            if not line:
                continue

            # Claude uses SSE format similar to OpenAI
            if line.startswith("data: "):
                data_str = line[6:]
                try:
                    data = orjson.loads(data_str)
                    self.debug_logger.log_chunk(data)

                    chunk = self._convert_claude_chunk(data, message_id, chunk_index)
                    if chunk:
                        chunk_index += 1
                        yield chunk
                except (orjson.JSONDecodeError, Exception) as e:
                    self.debug_logger.log_error(f"Failed to parse Claude chunk: {e}")
                    continue

    def _convert_claude_chunk(
        self, data: Dict[str, Any], message_id: str, _index: int
    ) -> Optional[ChatCompletionChunk]:
        """Convert Claude chunk format to our internal format"""
        event_type = data.get("type")

        # Handle different Claude event types
        if event_type == "content_block_delta":
            delta = data.get("delta", {})
            if delta.get("type") == "text_delta":
                return ChatCompletionChunk(
                    id=message_id,
                    object="chat.completion.chunk",
                    created=int(time.time()),
                    model=self.model,
                    choices=[
                        Choice(
                            index=0,
                            delta=Delta(content=delta.get("text", "")),
                            finish_reason=None,
                        )
                    ],
                )
        elif event_type == "message_start":
            # Initial message
            return ChatCompletionChunk(
                id=message_id,
                object="chat.completion.chunk",
                created=int(time.time()),
                model=self.model,
                choices=[
                    Choice(
                        index=0,
                        delta=Delta(role="assistant"),
                        finish_reason=None,
                    )
                ],
            )
        elif event_type == "message_stop":
            # Final message
            return ChatCompletionChunk(
                id=message_id,
                object="chat.completion.chunk",
                created=int(time.time()),
                model=self.model,
                choices=[
                    Choice(
                        index=0,
                        delta=Delta(),
                        finish_reason="stop",
                    )
                ],
            )
        else:
            return None


def create_client(
    provider: APIProvider,
    config: Optional[Dict[str, Any]] = None,
) -> BaseAPIClient:
    """Factory function to create the appropriate client based on provider"""
    config = config or {}

    if provider == APIProvider.JARVIS:
        return JarvisAPIClient(
            base_url=config.get("base_url", ""),
            user_id=config.get("user_id", ""),
            timeout=config.get("timeout", 120.0),
            jwt_token=config.get("jwt_token"),
            token_expires_at=config.get("token_expires_at"),
            on_token_refresh=config.get("on_token_refresh"),
        )
    elif provider == APIProvider.OPENAI:
        return OpenAIClient(
            api_key=config.get("api_key", ""),
            model=config.get("model", "gpt-4-turbo"),
            timeout=config.get("timeout", 120.0),
        )
    elif provider == APIProvider.CLAUDE:
        return ClaudeClient(
            api_key=config.get("api_key", ""),
            model=config.get("model", "claude-haiku-4-5-20251001"),
            timeout=config.get("timeout", 120.0),
        )
    else:
        raise ValueError(f"Unknown provider: {provider}")


# For backward compatibility
JarvisClient = JarvisAPIClient