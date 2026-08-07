"""
Model Client — provider-agnostic call layer.

Route every agent's LLM calls through this instead of importing a
provider SDK directly into agent logic. Swapping providers/models
becomes a config change, not a rewrite.

Usage:
    client = ModelClient(provider="anthropic", model="claude-sonnet-5")
    result = client.call_structured(
        system=TRIAGE_PROMPT,
        user_content=findings_json,
        schema=TriageFinding,
    )
"""

import json
import os
from dataclasses import dataclass
from typing import Type, TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


@dataclass
class ModelConfig:
    provider: str  # "anthropic" | "openai" | "google"
    model: str
    max_tokens: int = 4096


class ModelClient:
    def __init__(self, provider: str, model: str, max_tokens: int = 4096):
        self.config = ModelConfig(provider=provider, model=model, max_tokens=max_tokens)
        self._client = self._init_provider_client()

    def _init_provider_client(self):
        if self.config.provider == "anthropic":
            from anthropic import Anthropic
            return Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
        elif self.config.provider == "openai":
            from openai import OpenAI
            return OpenAI(api_key=os.environ["OPENAI_API_KEY"])
        elif self.config.provider == "google":
            import google.generativeai as genai
            genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
            return genai
        raise ValueError(f"Unknown provider: {self.config.provider}")

    def call_structured(self, system: str, user_content: str, schema: Type[T]) -> T:
        """
        Calls the configured model and validates the response against
        a pydantic schema. Raises if the model's output doesn't match
        the contract — fail loudly here, don't let malformed output
        propagate downstream.
        """
        raw_text = self._call_raw(system, user_content)
        parsed = json.loads(raw_text)
        return schema.model_validate(parsed)

    def _call_raw(self, system: str, user_content: str) -> str:
        if self.config.provider == "anthropic":
            response = self._client.messages.create(
                model=self.config.model,
                max_tokens=self.config.max_tokens,
                system=system,
                messages=[{"role": "user", "content": user_content}],
            )
            return response.content[0].text

        elif self.config.provider == "openai":
            response = self._client.chat.completions.create(
                model=self.config.model,
                max_tokens=self.config.max_tokens,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user_content},
                ],
            )
            return response.choices[0].message.content

        elif self.config.provider == "google":
            model = self._client.GenerativeModel(self.config.model)
            response = model.generate_content(f"{system}\n\n{user_content}")
            return response.text

        raise ValueError(f"Unknown provider: {self.config.provider}")


def load_prompt(name: str) -> str:
    """Load a prompt from the prompts/ directory rather than embedding
    it as a string in application code — makes prompt changes a content
    edit, not a deploy."""
    path = os.path.join(os.path.dirname(__file__), "prompts", f"{name}.txt")
    with open(path) as f:
        return f.read()
