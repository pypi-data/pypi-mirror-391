"""Utility classes and functions for building function arguments and decorators."""

from __future__ import annotations

from dataclasses import dataclass
from typing import NamedTuple

from funcy_bear.constants.characters import ASTERISK, AT, COLON, EQUALS, PIPE
from funcy_bear.type_stuffs.builtin_tools import type_name


class Arg(NamedTuple):
    """Represents a function argument with optional type annotation and default value."""

    name: str
    annotation: str | type | list[type] = ""
    default: str = ""
    arg: bool = False
    kwarg: bool = False

    @property
    def type(self) -> str:
        """Get the type annotation as a string.

        Returns:
            The type annotation as a string.
        """
        if isinstance(self.annotation, list):
            return f"{PIPE}".join(type_name(t) for t in self.annotation)
        return type_name(self.annotation)

    def render(self) -> str:
        """Render the argument to a string.

        Returns:
            The argument as a string.
        """
        s: str = f"{ASTERISK if self.arg else ASTERISK * 2 if self.kwarg else ''}{self.name}"
        if self.type:
            s += f"{COLON} {self.type}"
        if self.default:
            s += f" {EQUALS} {self.default}"
        return s


class Decorator(NamedTuple):
    """Represents a function decorator."""

    name: str
    args: str | Arg | list[Arg] = ""
    called: bool = False

    def render(self) -> str:
        """Render the decorator to a string.

        Returns:
            The decorator as a string.
        """
        from .helpers import render_args  # noqa: PLC0415

        args_str: str = render_args(self.args) if self.args else ""
        return f"{AT}{self.name}{f'({args_str})' if self.called or args_str else ''}"


class Variable(NamedTuple):
    """Represents a variable with optional type annotation and default value."""

    name: str
    annotation: str | type | list[type] = ""
    default: str = ""

    @property
    def type(self) -> str:
        """Get the type annotation as a string.

        Returns:
            The type annotation as a string.
        """
        if isinstance(self.annotation, list):
            return f"{PIPE}".join(type_name(t) for t in self.annotation)
        return type_name(self.annotation)

    def render(self) -> str:
        """Render the variable to a string.

        Returns:
            The variable as a string.
        """
        s: str = f"{self.name}"
        if self.type:
            s += f"{COLON} {self.type}"
        if self.default:
            s += f" {EQUALS} {self.default}"
        return s


@dataclass(slots=True)
class Docstring:
    """Represents a docstring."""

    content: str

    def add(self, additional_content: str, prefix: str = "", suffix: str = "") -> Docstring:
        """Add additional content to the docstring.

        Args:
            additional_content: The content to add to the docstring.
            prefix: An optional prefix to add before the additional content.
            suffix: An optional suffix to add after the additional content.

        Returns:
            The updated Docstring instance.
        """
        self.content += f"{prefix}{additional_content}{suffix}"
        return self

    def render(self) -> str:
        """Render the docstring to a string.

        Returns:
            The docstring as a string.
        """
        from .helpers import get_docstring  # noqa: PLC0415

        return get_docstring(self.content)

    def clear(self) -> Docstring:
        """Clear the docstring content.

        Returns:
            The updated Docstring instance.
        """
        self.content = ""
        return self
