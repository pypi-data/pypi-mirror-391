"""Prompt configuration for the sequential agent."""

from .base import BasePrompt


class TestSeqPrompt(BasePrompt):
    """Prompt describing the sequential agent coordination."""

    @property
    def system_role(self) -> str:
        """Return the role presented to the sequential agent.

        Returns:
            str: Role description declared to the model.
        """
        return "Agente sequencial de ADK"

    @property
    def system_instructions(self) -> str:
        """Return the coordination instructions for the sequential agent.

        Returns:
            str: Instruction text directing message forwarding.
        """
        return "Pasar el mensaje del usuario al siguiente agente en la secuencia."
