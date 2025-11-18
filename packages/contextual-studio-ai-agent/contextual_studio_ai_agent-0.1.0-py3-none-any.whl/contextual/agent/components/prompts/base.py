"""Base prompt abstractions for contextual agents."""

from abc import ABC, abstractmethod

PromptParts = dict[str, str | None]


class BasePrompt(ABC):
    """Define the structure and rendering helpers for agent prompts."""

    @property
    def name(self) -> str:
        """Return the prompt identifier.

        Returns:
            str: Class name used as the prompt name.
        """
        return self.__class__.__name__

    # ==========================================================
    # SYSTEM
    # ==========================================================

    @property
    @abstractmethod
    def system_role(self) -> str:
        """Return the role assumed by the agent.

        Returns:
            str: Role description presented to the model.
        """
        pass

    @property
    @abstractmethod
    def system_instructions(self) -> str:
        """Return the core system instructions.

        Returns:
            str: Guidance that drives the agent behavior.
        """
        pass

    @property
    def system_context(self) -> str | None:
        """Return additional context for the agent.

        Returns:
            str | None: Optional background information available to the agent.
        """
        return None

    @property
    def system_examples(self) -> str | None:
        """Return illustrative interaction examples.

        Returns:
            str | None: Few-shot examples or ``None`` when not provided.
        """
        return None

    @property
    def system_extra_info(self) -> str | None:
        """Return additional metadata or constraints.

        Returns:
            str | None: Supplemental information or ``None`` when absent.
        """
        return None

    @property
    def input_parameters(self) -> dict[str, str] | None:
        """Return the expected user parameters.

        Returns:
            dict[str, str] | None: Mapping of parameter names to descriptions.
        """
        return None

    @property
    def system_message(self) -> PromptParts:
        """Compose the full system message.

        Returns:
            PromptParts: Dictionary with role, instructions, and related sections.
        """
        return {
            "role": self.system_role,
            "instructions": self.system_instructions,
            "context": self.system_context,
            "examples": self.system_examples,
            "extra information": self.system_extra_info,
        }

    @property
    def parameters(self) -> PromptParts | None:
        """Compose the input and output parameter sections.

        Returns:
            PromptParts | None: Dictionary of parameters or ``None`` when absent.
        """
        if self.input_parameters is None:
            return None
        return {
            "input": self._parameters_to_str(self.input_parameters),
        }

    # ==========================================================
    # HELPER METHODS
    # ==========================================================

    def _parameters_to_str(self, parameters: dict[str, str] | None) -> str:
        """Convert the parameter mapping into a markdown-friendly string.

        Args:
            parameters: Mapping of parameter names to descriptions.

        Returns:
            str: Rendered parameter definitions joined by blank lines.
        """
        if parameters is None:
            return ""
        return "\n\n".join([f"{val}\n{{{key}}}" for key, val in parameters.items()])

    # ==========================================================
    # RENDER METHODS
    # ==========================================================

    def _render_parts_to_md(self, data: dict[str, str | None], depth: int = 3) -> str:
        """Render a nested dictionary into Markdown headers and blocks.

        Args:
            data: Nested dictionary representing prompt sections.
            depth: Heading depth (###, ####, etc.) to apply to top-level keys.

        Returns:
            str: Markdown representation of the provided parts.
        """
        if not data:
            return ""

        markdown_parts = []
        header_prefix = "#" * depth

        for key, value in data.items():
            if value is None or value == "":
                continue

            if isinstance(value, dict):
                # Renderizado recursivo
                markdown_parts.append(f"{header_prefix} {key.upper()}\n")
                markdown_parts.append(self._render_parts_to_md(value, depth + 1))
            else:
                markdown_parts.append(f"{header_prefix} {key.upper()}\n```\n{value}\n```")

        return "\n\n".join(markdown_parts)

    def to_markdown(self) -> str:
        """Render the prompt sections into a human-readable Markdown string.

        Returns:
            str: Markdown content describing the system message and parameters.
        """
        delimiter: str = "\n"
        system_header: str = "# SYSTEM"
        system_md: str = (
            f"{system_header}{delimiter}{self._render_parts_to_md(self.system_message, depth=2)}"
        )

        if self.parameters is None:
            return delimiter + system_md + delimiter

        parameters_header: str = "# PARAMETERS"
        parameters_md: str = (
            f"{parameters_header}{delimiter}{self._render_parts_to_md(self.parameters, depth=2)}"
        )
        return delimiter + system_md + delimiter + delimiter + parameters_md + delimiter
