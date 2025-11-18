"""Agent implementation for handling Test A prompt interactions."""

from functools import cached_property
from typing import Any

from google.adk.agents import Agent
from pydantic import BaseModel

from ...factories import LLMfactory
from ...models import LlmModel
from ..prompts import BasePrompt, TestAPrompt
from .base import BaseAgent


class OutputSchema(BaseModel):
    """Schema describing the agent response payload."""

    respuesta: str


class ADKAgent(BaseAgent[Agent, Any]):
    """Agent backed by the Gemini ADK client using the Test A prompt."""

    @property
    def prompt(self) -> BasePrompt:
        """Return the configured Test A prompt.

        Returns:
            BasePrompt: Prompt instance describing the agent behavior.
        """
        return TestAPrompt()

    @property
    def tools(self) -> Any | None:
        """Return the optional toolset for the agent.

        Returns:
            Any | None: Tool definitions or ``None`` when no tools are required.
        """
        return None

    @property
    def model(self) -> LlmModel:
        """Return the Gemini model configuration.

        Returns:
            LlmModel: Language model configuration used by the agent.
        """
        return LlmModel(model_name="gemini-2.5-flash")

    @property
    def output_key(self) -> str | None:
        """Return the response field key.

        Returns:
            str | None: Key used to extract the agent answer.
        """
        return "respuesta"

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

        if self.output_schema is not None:
            return Agent(
                name=self.name,
                description=self.description,
                instruction=self.prompt.to_markdown(),
                model=LLMfactory.create(self.model),
                output_schema=self.output_schema,
                disallow_transfer_to_parent=True,
                disallow_transfer_to_peers=True,
            )
        return Agent(
            name=self.name,
            description=self.description,
            instruction=self.prompt.to_markdown(),
            model=LLMfactory.create(self.model),
            input_schema=self.input_schema,
            output_key=self.output_key,
        )
