"""Content and role models exchanged with Gemini ADK."""

from datetime import datetime
from enum import Enum

from google.genai import types
from pydantic import BaseModel, Field


class RoleType(str, Enum):
    """Enumerates the possible roles for a conversation participant."""

    USER = "user"
    MODEL = "model"
    UNKNOWN = "unknown"


class Part(BaseModel):
    """Represents a single text fragment within a message."""

    text: str = Field(..., description="The text content of the part.")


class Content(BaseModel):
    """Conversation content exchanged with the Gemini APIs."""

    role: RoleType = Field(..., description="The role of the message sender.")
    parts: list[Part] = Field(..., description="The parts.")
    timestamp: datetime = Field(
        default_factory=datetime.now, description="The timestamp of when the message was created."
    )

    def to_adk_content(self) -> types.Content:
        """Convert the content into the ADK wire format.

        Returns:
            types.Content: Gemini ADK content payload.
        """
        return types.Content(
            role=self.role.value, parts=[types.Part(text=part.text) for part in self.parts]
        )

    @classmethod
    def from_adk_content(cls, adk_content: types.Content) -> "Content":
        """Create a contextual content instance from an ADK payload.

        Args:
            adk_content: Content instance produced by the ADK runner.

        Returns:
            Content: Local representation containing the converted parts.
        """
        return cls(
            role=RoleType(adk_content.role) if adk_content.role else RoleType.UNKNOWN,
            parts=[
                Part(text=part.text)
                for part in adk_content.parts
                if adk_content.parts and part.text
            ],
            timestamp=datetime.now(),
        )
