import httpx
import orjson
from typing import AsyncIterator, List, Optional
from .models import (
    ChatCompletionRequest,
    ChatCompletionChunk,
    Message,
    JarvisOptions,
)
from .logger import get_debug_logger


class JarvisClient:
    def __init__(
        self,
        base_url: str,
        user_id: str,
        jarvis_options: Optional[JarvisOptions] = None,
        timeout: float = 120.0,
    ):
        self.base_url = base_url.rstrip("/")
        self.user_id = user_id
        self.jarvis_options = jarvis_options or JarvisOptions()
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=timeout)

    async def close(self) -> None:
        await self.client.aclose()

    async def chat_completion_stream(
        self,
        messages: List[Message],
        conversation_id: Optional[str] = None,
    ) -> AsyncIterator[ChatCompletionChunk]:
        debug_logger = get_debug_logger()
        
        jarvis_options = self.jarvis_options.model_copy()
        if conversation_id:
            jarvis_options.conversation_id = conversation_id

        request = ChatCompletionRequest(
            model="jarvis-chat",
            messages=messages,
            stream=True,
            user=self.user_id,
            jarvis_options=jarvis_options,
        )

        url = f"{self.base_url}/chat/completions"
        
        debug_logger.log_request({
            "url": url,
            "messages": [m.model_dump() for m in messages],
            "conversation_id": conversation_id,
            "jarvis_options": jarvis_options.model_dump()
        })

        try:
            async with self.client.stream(
                "POST",
                url,
                json=request.model_dump(),
                headers={"Content-Type": "application/json"},
            ) as response:
                response.raise_for_status()
                async for chunk in self._parse_sse_stream(response):
                    yield chunk
        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP error {e.response.status_code}: {e.response.text}"
            debug_logger.log_error(error_msg)
            raise RuntimeError(error_msg)
        except Exception as e:
            error_msg = f"Failed to stream chat completion: {e}"
            debug_logger.log_error(error_msg)
            raise RuntimeError(error_msg)

    async def _parse_sse_stream(
        self, response: httpx.Response
    ) -> AsyncIterator[ChatCompletionChunk]:
        debug_logger = get_debug_logger()
        
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
                    debug_logger.log_chunk(data)
                    chunk = ChatCompletionChunk(**data)
                    yield chunk
                except (orjson.JSONDecodeError, Exception):
                    continue
