"""Agent implementation for transforming responses with the Test B prompt."""

from functools import cached_property
from typing import Any

from google.adk.agents import Agent

from ...factories import LLMfactory
from ...models import LlmModel
from ..prompts import BasePrompt, TestBPrompt
from .base import BaseAgent


class ADKBAgent(BaseAgent[Agent, Any]):
    """Agent that transforms responses using an uppercase prompt."""

    @property
    def prompt(self) -> BasePrompt:
        """Return the configured Test B prompt.

        Returns:
            BasePrompt: Prompt instance enforcing uppercase responses.
        """
        return TestBPrompt()

    @property
    def tools(self) -> Any | None:
        """Return the optional toolset for the agent.

        Returns:
            Any | None: Tool definitions or ``None`` when not required.
        """
        return None

    @property
    def model(self) -> LlmModel:
        """Return the Gemini model configuration.

        Returns:
            LlmModel: Language model configuration used by the agent.
        """
        return LlmModel(model_name="gemini-2.5-flash")

    @cached_property
    def client(self) -> Agent:
        """Instantiate the underlying ADK agent client.

        Returns:
            Agent: Configured Gemini ADK agent client.
        """
        if self.tools is not None:
            return Agent(
                name=self.name,
                description=self.description,
                instruction=self.prompt.to_markdown(),
                model=LLMfactory.create(self.model),
                tools=self.tools,
                output_key=self.output_key,
            )
        return Agent(
            name=self.name,
            description=self.description,
            instruction=self.prompt.to_markdown(),
            model=LLMfactory.create(self.model),
            input_schema=self.input_schema,
            output_schema=self.output_schema,
            output_key=self.output_key,
        )
