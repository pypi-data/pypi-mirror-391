"""Factories to build Gemini Lite LLM clients."""

from google.adk.models.lite_llm import LiteLlm

from ..models import LlmModel


class LLMfactory:
    """Factory that instantiates LiteLlm clients from model definitions."""

    @staticmethod
    def create(model: LlmModel) -> LiteLlm:
        """Create a LiteLlm client for the provided model configuration.

        Args:
            model: Language model settings describing the Gemini model.

        Returns:
            LiteLlm: Client ready to interact with the Gemini backend.
        """
        return LiteLlm(model=model.model_name)
