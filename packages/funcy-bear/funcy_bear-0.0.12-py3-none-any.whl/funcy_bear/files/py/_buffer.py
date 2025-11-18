from io import StringIO
from typing import Self

from funcy_bear.constants.characters import INDENT
from funcy_bear.ops.math import clamp


class BufferHelper:
    """Dataclass representing a section of a code buffer."""

    def __init__(self, buffer: StringIO | None = None, indent: int = 0, content: str = "") -> None:
        """Initialize a BufferSection.

        Args:
            indent: The initial indentation level.
        """
        self.indent: int = indent
        self._data: StringIO = buffer or StringIO()
        if content:
            self._data.write(content)

    def write(self, line: str, prefix: str = "", suffix: str = "") -> Self:
        """Add a line to the buffer with the current indentation.

        Args:
            line: The line to add to the buffer.
            prefix: Optional prefix to add before the line.
            suffix: Optional suffix to add after the line.
        """
        indented_line: str = INDENT * self.indent + line
        self._data.write(f"{prefix}{indented_line}{suffix}")
        return self

    def tick(self) -> Self:
        """Increase the indentation level by one."""
        self.indent += 1
        return self

    def tock(self) -> Self:
        """Decrease the indentation level by one, not going below zero."""
        self.indent = clamp(self.indent - 1, 0, self.indent)
        return self

    def clear(self) -> Self:
        """Clear the buffer content."""
        self._data.seek(0)
        self._data.truncate(0)
        return self

    def getvalue(self) -> str:
        """Get the current content of the buffer.

        Returns:
            The content of the buffer as a string.
        """
        value: str = self._data.getvalue()
        return value

    @property
    def not_empty(self) -> bool:
        """Check if the buffer has any content.

        Returns:
            True if the buffer is not empty, False otherwise.
        """
        return bool(self._data.getvalue())

    def close(self) -> None:
        """Close the underlying buffer."""
        self._data.close()

    def __str__(self) -> str:
        """Return the string representation of the buffer content.

        Returns:
            The content of the buffer as a string.
        """
        return self.getvalue()

    def __repr__(self) -> str:
        """Return the official string representation of the BufferHelper.

        Returns:
            A string representation of the BufferHelper.
        """
        return f"BufferHelper(indent={self.indent}, content={self.getvalue()!r})"

    def __enter__(self) -> Self:
        """Enter the runtime context related to this object.

        Returns:
            The BufferHelper instance.
        """
        return self

    def __exit__(self, exc_type: object, exc_value: object, traceback: object) -> None:
        """Exit the runtime context related to this object.

        Args:
            exc_type: The exception type.
            exc_value: The exception value.
            traceback: The traceback object.
        """
        self.close()
