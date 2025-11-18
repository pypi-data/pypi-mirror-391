"""Prompt configuration for the Test B agent."""

from .base import BasePrompt


class TestBPrompt(BasePrompt):
    """Prompt that transforms agent responses to uppercase."""

    @property
    def system_role(self) -> str:
        """Return the role presented to the Test B agent.

        Returns:
            str: Role description declared to the model.
        """
        return "Asistente de IA"

    @property
    def system_instructions(self) -> str:
        """Return the transformation instructions.

        Returns:
            str: Instruction text enforcing uppercase responses.
        """
        return "Transforma la respuesta del agente a mayusculas."

    @property
    def system_examples(self) -> str:
        """Return illustrative examples for the transformation.

        Returns:
            str: Example demonstrating uppercase output.
        """
        return "Respuesta agente a: 'Hoy es martes'\nRespuesta: 'HOY ES MARTES'"

    @property
    def input_parameters(self) -> dict[str, str] | None:
        """Return the expected input parameters for the agent.

        Returns:
            dict[str, str] | None: Mapping with the `respuesta` parameter.
        """
        return {"respuesta": "La respuesta generada por el agente a."}
