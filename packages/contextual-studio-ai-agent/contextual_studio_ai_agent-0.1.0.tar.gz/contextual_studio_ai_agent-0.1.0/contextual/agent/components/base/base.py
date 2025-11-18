"""Core abstractions for contextual agent implementations."""

from abc import ABC, abstractmethod
from functools import cached_property
from typing import Generic, TypeVar

from pydantic import BaseModel

from ...models import LlmModel
from ..prompts import BasePrompt

T = TypeVar("T")
S = TypeVar("S")


class BaseAgent(ABC, Generic[T, S]):
    """Abstract base class for agent implementations."""

    @property
    def name(self) -> str:
        """Return the agent identifier.

        Returns:
            str: Class name used as the agent name.
        """
        return self.__class__.__name__

    @property
    @abstractmethod
    def prompt(self) -> BasePrompt:
        """Return the prompt configuration for the agent.

        Returns:
            BasePrompt: Prompt instance describing the agent behavior.
        """
        pass

    @property
    def tools(self) -> S | None:
        """Return the tool configuration for the agent.

        Returns:
            S | None: Tool definitions or ``None`` when no tools are set.
        """
        return None

    @property
    def description(self) -> str:
        """Return the agent description derived from the prompt.

        Returns:
            str: Human readable description of the agent.
        """
        return self.prompt.system_role

    @property
    def model(self) -> LlmModel | None:
        """Return the language model configuration.

        Returns:
            LlmModel | None: Model definition or ``None`` if not configured.
        """
        return None

    @property
    def input_schema(self) -> BaseModel | None:
        """Return the input schema accepted by the agent.

        Returns:
            BaseModel | None: Pydantic schema for inputs or ``None`` if unchecked.
        """
        return None

    @property
    def output_schema(self) -> BaseModel | None:
        """Return the output schema produced by the agent.

        Returns:
            BaseModel | None: Pydantic schema describing outputs or ``None``.
        """
        return None

    @property
    def output_key(self) -> str | None:
        """Return the primary output key for structured responses.

        Returns:
            str | None: Key used to extract outputs or ``None`` if not applicable.
        """
        return None

    @cached_property
    @abstractmethod
    def client(self) -> T:
        """Return the underlying client implementation.

        Returns:
            T: Instantiated agent client.
        """
        pass
