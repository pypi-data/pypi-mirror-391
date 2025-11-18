"""Agent that orchestrates the Test A and Test B agents sequentially."""

from functools import cached_property
from typing import Any

from google.adk.agents import SequentialAgent

from ..base import ADKAgent, ADKBAgent, BaseAgent
from ..prompts import BasePrompt, TestSeqPrompt


class ADKSequentialAgent(BaseAgent[SequentialAgent, Any]):
    """Agent that chains the Test A and Test B agents."""

    @property
    def name(self) -> str:
        """Return the agent identifier.

        Returns:
            str: Class name used as the agent name.
        """
        return self.__class__.__name__

    @property
    def prompt(self) -> BasePrompt:
        """Return the configured sequential prompt.

        Returns:
            BasePrompt: Prompt instance describing the sequential behavior.
        """
        return TestSeqPrompt()

    @property
    def description(self) -> str:
        """Return the agent description derived from the prompt.

        Returns:
            str: Human readable description of the agent.
        """
        return self.prompt.system_role

    @cached_property
    def client(self) -> SequentialAgent:
        """Instantiate the sequential agent client.

        Returns:
            SequentialAgent: Configured Gemini ADK sequential agent.
        """
        return SequentialAgent(
            name=self.name,
            description=self.description,
            sub_agents=[ADKAgent().client, ADKBAgent().client],
            before_agent_callback=None,
            after_agent_callback=None,
        )
