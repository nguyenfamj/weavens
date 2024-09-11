import json
from typing import AsyncGenerator

import httpx


class GraphClient:
    """Client for interacting with the graph"""

    def __init__(
        self, base_url: str = "http://localhost:8686", timeout: float | None = None
    ):
        self.base_url = base_url
        self.time_out = timeout

    def _parse_stream_line(self, line: str) -> str | None:
        line = line.strip()
        if line.startswith("data: "):
            data = line[6:]
            if data == "[DONE]":
                return None
            try:
                parsed = json.loads(data)
            except Exception as e:
                raise Exception("Error JSON parsing message from server %e" % e)
            match parsed.get("type"):
                case "message":
                    return parsed["content"]
                case "token":
                    return parsed["content"]
                case "error":
                    raise Exception(parsed["content"])

    async def astream(
        self, message: str, thread_id: str, stream_tokens: bool = True
    ) -> AsyncGenerator[str, None]:
        payload = {
            "message": message,
            "thread_id": thread_id,
            "stream_tokens": stream_tokens,
        }

        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/api/v1/graph/stream",
                json=payload,
                timeout=self.time_out,
            ) as response:
                if response.status_code != 200:
                    raise Exception(f"Error: {response.status_code}")
                async for line in response.aiter_lines():
                    if line.strip():
                        parsed = self._parse_stream_line(line)
                        if parsed is None:
                            break
                        yield parsed
