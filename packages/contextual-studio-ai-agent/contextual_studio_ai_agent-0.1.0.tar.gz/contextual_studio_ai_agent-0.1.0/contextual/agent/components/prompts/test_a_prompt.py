"""Prompt configuration for the Test A agent."""

from .base import BasePrompt


class TestAPrompt(BasePrompt):
    """Prompt that guides the base agent to answer accurately."""

    @property
    def system_instructions(self) -> str:
        """Return the core instructions for the Test A agent.

        Returns:
            str: Instruction text emphasizing accurate answers.
        """
        return "Responde con precisión y evita inventar información."

    @property
    def system_role(self) -> str:
        """Return the role presented to the Test A agent.

        Returns:
            str: Role description declared to the model.
        """
        return "Asistente de IA"

    @property
    def system_context(self) -> str:
        """Return the conversation context for the Test A agent.

        Returns:
            str: Context describing the user interaction.
        """
        return "Conversación con un usuario"

    @property
    def system_examples(self) -> str:
        """Return illustrative examples for the Test A agent.

        Returns:
            str: Few-shot dialogue demonstrating expected behavior.
        """
        return "Usuario: ¿Qué es un agente React?\nAgente: Es un agente basado en razonamiento iterativo."
