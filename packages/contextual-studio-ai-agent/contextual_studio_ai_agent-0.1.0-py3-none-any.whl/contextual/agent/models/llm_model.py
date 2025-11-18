"""Language model descriptors for contextual agents."""

from pydantic import BaseModel


class LlmModel(BaseModel):
    """Configuration describing a Gemini model selection."""

    model_name: str
