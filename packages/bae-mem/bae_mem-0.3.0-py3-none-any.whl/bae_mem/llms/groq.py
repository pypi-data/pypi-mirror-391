import json
import os
from typing import Dict, List, Optional

import httpx

from bae_mem.configs.llms.base import BaseLlmConfig
from bae_mem.llms.base import LLMBase
from bae_mem.memory.utils import extract_json


class GroqLLM(LLMBase):
    def __init__(self, config: Optional[BaseLlmConfig] = None):
        super().__init__(config)

        if not self.config.model:
            self.config.model = "llama3-70b-8192"

        self.api_key = self.config.api_key or os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY is required for Groq LLM usage.")

        self.base_url = os.getenv("GROQ_API_BASE", "https://api.groq.com/openai/v1")
        self._client = httpx.Client(
            base_url=self.base_url,
            headers={"Authorization": f"Bearer {self.api_key}"},
            timeout=60,
        )

    def _parse_response(self, response: Dict, tools):
        """
        Process the response based on whether tools are used or not.

        Args:
            response: The raw response from API.
            tools: The list of tools provided in the request.

        Returns:
            str or dict: The processed response.
        """
        choices = response.get("choices", [])
        if not choices:
            return None

        message = choices[0].get("message", {})
        content = message.get("content")
        tool_calls = message.get("tool_calls") or []

        if tools:
            processed_response = {
                "content": content,
                "tool_calls": [],
            }

            if tool_calls:
                for tool_call in tool_calls:
                    function = tool_call.get("function", {})
                    processed_response["tool_calls"].append(
                        {
                            "name": function.get("name"),
                            "arguments": json.loads(extract_json(function.get("arguments", "{}"))),
                        }
                    )

            return processed_response
        else:
            return content

    def generate_response(
        self,
        messages: List[Dict[str, str]],
        response_format=None,
        tools: Optional[List[Dict]] = None,
        tool_choice: str = "auto",
    ):
        """
        Generate a response based on the given messages using Groq.

        Args:
            messages (list): List of message dicts containing 'role' and 'content'.
            response_format (str or object, optional): Format of the response. Defaults to "text".
            tools (list, optional): List of tools that the model can call. Defaults to None.
            tool_choice (str, optional): Tool choice method. Defaults to "auto".

        Returns:
            str: The generated response.
        """
        params = {
            "model": self.config.model,
            "messages": messages,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
            "top_p": self.config.top_p,
            "response_format": response_format,
            "stream": False,
        }

        if response_format is None:
            params.pop("response_format")

        if tools:
            params["tools"] = tools
            params["tool_choice"] = tool_choice

        response = self._client.post("/chat/completions", json=params)
        response.raise_for_status()
        response_data = response.json()
        return self._parse_response(response_data, tools)
