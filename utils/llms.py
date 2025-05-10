"""Wrappers for OpenAI Chat Completions and MLFlow model serving API calls."""

from dotenv import load_dotenv
import os
import json
import logging
import requests

import openai


load_dotenv()

log = logging.getLogger(__name__)


class CustomOpenAIClient:
    """OpenAI Chat Completions API wrapper."""

    def __init__(
        self,
        model: str = os.getenv("LLM_MODEL_NAME"),
        max_tokens: int = 512,
        temperature: float = 0.8,
        top_p: float = 0.9,
        enable_streaming: bool = False,
    ):
        """Initialize the client.

        Args:
            model (str, optional): model name to use for completions. Defaults to os.getenv("LLM_MODEL_NAME").
            max_tokens (int, optional): Truncation threshold for model responses. Defaults to 512.
            temperature (float, optional): Model likelihood of selecting less probable tokens. Defaults to 0.8.
            top_p (float, optional): Model cumulative probability cutoff for token selection. Defaults to 0.9.
            enable_streaming (bool, optional): Determines if the chat completions endpoint will return the full
                response or yield a generator. Defaults to False.
        """
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.top_p = top_p
        self.enable_streaming = enable_streaming
        self.client = openai.OpenAI(
            api_key=os.getenv("LLM_API_KEY"),
            base_url=os.getenv("LLM_BASE_URL"),
        )

    def generate(self, messages: list[dict], tools: list[str] = None):
        """Gets response from the `chat/completions` endpoint.

        Args:
            messages (list[dict]): A list of messages. Each message is a dictionary with a "role" and "content" key.
                The "role" can be "user", "assistant", or "system". The "content" is the text of the message.
                The list of messages should be in the order they were sent. The first message should be the system message,
                followed by the user message, and then the assistant message.
            tools (list[str], optional): A list of tools to use for the generating tool calls. Defaults to None.

        Either returns a string or yields a generator object, depending on the value of `enable_streaming`.
        """
        chat_completion = self.client.chat.completions.create(
            model=self.model,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            top_p=self.top_p,
            stream=self.enable_streaming if not tools else False,  # Disable streaming if tools are used
            messages=messages,
            tools=tools,
        )
        log.debug("Generating response; prompt= %s", messages)
        if tools:
            log.debug("Tools enabled. Returning raw result: %s.", chat_completion)
            return chat_completion
        if self.enable_streaming:
            log.debug("Streaming response enabled. Returning generator.")
            return chat_completion
        else:
            response_string = chat_completion.choices[0].message.content
            log.debug("Returning result as string only: %s.", response_string)
            return response_string


class TextClassifier:
    def __init__(
        self,
        model_url: str = os.getenv("CLASSIFIER_URL"),
        headers: dict[str, str] = {"Content-Type": "application/json"},
    ):
        self.model_url = model_url
        self.headers = headers

    def classify(self, query: str|list[str]) -> dict[str, list[dict[str, str|float]]]:
        """Classifies query using the selected classifier model."""
        response = requests.post(
            url=f"http://localhost:5001/invocations",
            data=json.dumps({"inputs": query}),
            headers={"Content-Type": "application/json"},
        )
        return response.json()