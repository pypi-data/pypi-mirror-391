"""Base manager abstractions for orchestrating ADK runners."""

from abc import ABC, abstractmethod
from typing import AsyncGenerator, Generic, Self, TypeVar

from loguru import logger
from pydantic import BaseModel, PrivateAttr

from ..models import Content, Part, RoleType

T = TypeVar("T")
E = TypeVar("E")


class BaseManager(BaseModel, ABC, Generic[T, E]):
    """Abstract base class that coordinates ADK runners and events."""

    _runner: T | None = PrivateAttr(default=None)

    async def ainvoke(self, input: Content, user_id: str, session_id: str) -> Content:
        """Invoke the manager asynchronously.

        Template method.

        Args:
            input: Conversation content to send to the runner.
            user_id: Identifier for the requesting user.
            session_id: Identifier for the chat session.

        Returns:
            Content: Final response produced by the runner.

        Raises:
            ValueError: If the runner has not been configured.
        """
        if self._runner is None:
            logger.error("Runner has not been set. Please set the runner before invoking.")
            raise ValueError("Runner has not been set. Please set the runner before invoking.")

        generator: AsyncGenerator[E, None] = self._get_event_generator(
            user_id=user_id, session_id=session_id, input=input
        )
        async for event in generator:
            logger.debug(f"[Event] :\n{event}")
            response: Content | None = self._process_event(event)
            if response is not None:
                break

        return (
            response
            if response is not None
            else Content(role=RoleType.UNKNOWN, parts=[Part(text="No response generated.")])
        )

    @abstractmethod
    def set_runner(self, runner: T) -> Self:
        """Attach the runner implementation to the manager.

        Args:
            runner: Runner instance that produces events for the manager.

        Returns:
            Self: Manager instance for chaining.
        """
        pass

    @abstractmethod
    def _get_event_generator(
        self, user_id: str, session_id: str, input: Content
    ) -> AsyncGenerator[E, None]:
        """Yield events produced by the runner.

        Args:
            user_id: Identifier for the requesting user.
            session_id: Identifier for the chat session.
            input: Content to forward to the runner.

        Yields:
            AsyncGenerator[E, None]: Stream of runner events.
        """
        pass

    @abstractmethod
    def _process_event(self, event: E) -> Content | None:
        """Return the accumulated response once the runner emits a final event.

        Args:
            event: Runner event emitted during execution.

        Returns:
            Content | None: Response content when finalised, otherwise ``None``.
        """
        pass
