"""Manager that captures the first response produced by a sequential runner."""

from typing import AsyncGenerator, Self

from google.adk.events import Event
from google.adk.runners import Runner
from google.genai import types
from pydantic import Field

from ..models import Content
from .base import BaseManager


class ADKSeqManager(BaseManager[Runner, Event]):
    """Manager that returns the response emitted by the last sequential agent."""

    last_agent_name: str = Field(..., description="Último agente que respondió.")

    def set_runner(self, runner: Runner) -> Self:
        """Attach the sequential ADK runner to the manager.

        Args:
            runner: Gemini ADK sequential runner instance.

        Returns:
            Self: Manager instance for chaining.
        """
        self._runner = runner
        return self

    def _process_event(self, event: Event) -> Content | None:
        """Convert events into contextual content when the target agent responds.

        Args:
            event: ADK event emitted by the runner.

        Returns:
            Content | None: Final response content or ``None`` when awaiting other agents.
        """
        if event.author == self.last_agent_name:
            return Content.from_adk_content(event.content)
        return None

    def _get_event_generator(
        self, user_id: str, session_id: str, input: Content
    ) -> AsyncGenerator[Event, None]:
        """Stream events from the ADK runner.

        Args:
            user_id: Identifier for the requesting user.
            session_id: Identifier for the chat session.
            input: Initial message to send to the runner.

        Yields:
            AsyncGenerator[Event, None]: Stream of ADK events.
        """
        adk_content: types.Content = input.to_adk_content()
        if self._runner is not None:
            gen: AsyncGenerator[Event, None] = self._runner.run_async(
                user_id=user_id, session_id=session_id, new_message=adk_content
            )
            return gen
        else:
            raise AttributeError("Runner must be set using set_runner method")
