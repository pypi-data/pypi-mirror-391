"""A simple in-memory string buffer that helps with dynamically creating files."""

from __future__ import annotations

from contextlib import contextmanager
from types import NoneType
from typing import TYPE_CHECKING, Any, Literal, Self

from funcy_bear.constants.characters import ARROW, COLON, ELLIPSIS, EMPTY_STRING, INDENT, NEWLINE

from ._buffer import BufferHelper
from ._protocols import CodeBuilder
from .helpers import Arg, Decorator, get_decorators, get_returns, render_args
from .parts import Docstring

if TYPE_CHECKING:
    from collections.abc import Generator

Sections = Literal["header", "imports", "type_checking", "body", "footer"]


class FunctionBuilder(CodeBuilder):
    """Builder for Python function definitions."""

    def __init__(
        self,
        name: str,
        indent: int = 0,
        args: str | Arg | list[Arg] = EMPTY_STRING,
        returns: str | type | tuple[type, ...] = NoneType,
        decorators: list[str] | list[Decorator] | None = None,
        docstring: str = EMPTY_STRING,
        body: str = EMPTY_STRING,
    ) -> None:
        """Initialize a FunctionBuilder.

        Args:
            name: Function name.
            args: Function arguments (without parentheses).
            returns: Optional return type annotation.
            decorators: Optional list of decorator strings (without @).
            indent: Base indentation level.
        """
        self.name: str = name
        self.args: str = render_args(args)
        self.returns: str = get_returns(returns, prefix=f" {ARROW} ", suffix=COLON)
        self._decorators: str = get_decorators(decorators) if decorators else EMPTY_STRING
        self._docstring: Docstring = Docstring(docstring)
        self._added_lines: BufferHelper = BufferHelper(indent=indent + 1)
        self._added_lines.write(body, suffix=NEWLINE) if body else None
        self._body: BufferHelper = BufferHelper(indent=indent + 1)
        self._result: BufferHelper = BufferHelper()

    @property
    def signature(self) -> str:
        """Set or update the function signature.

        Returns:
            string representing the function signature.
        """
        return f"def {self.name}({self.args}){self.returns}"

    def render(self) -> str:
        """Render the function to a string.

        Returns:
            The complete function definition as a string.
        """
        if self._decorators:
            self._result.write(self._decorators, suffix=NEWLINE)
        self._result.write(self.signature, suffix=NEWLINE)
        if self._docstring:
            self._body.write(self._docstring.render(), suffix=NEWLINE)
        self._result.write(self._body.getvalue())
        if self._added_lines.not_empty:
            self._result.write(self._added_lines.getvalue())
        else:
            self._body.write(ELLIPSIS)
            self._result.write(self._body.getvalue())
        result: str = self._result.getvalue()
        self.clear()
        return result

    def clear(self) -> Self:
        """Clear the function body and docstring."""
        self.name = EMPTY_STRING
        self.args = EMPTY_STRING
        self.returns = EMPTY_STRING
        self._decorators = EMPTY_STRING
        self._docstring.clear()
        self._body.clear()
        self._result.clear()
        self._added_lines.clear()
        return self


class ClassBuilder(CodeBuilder):
    """Builder for Python class definitions."""

    def __init__(
        self,
        name: str,
        indent: int = 0,
        bases: str | list[str] = EMPTY_STRING,
        type_p: str | list[str] = EMPTY_STRING,
        decorators: list[str] | list[Decorator] | None = None,
        docstring: str = EMPTY_STRING,
        body: str = EMPTY_STRING,
    ) -> None:
        """Initialize a ClassBuilder.

        Args:
            name: Class name.
            bases: Optional base classes (without parentheses).
            decorators: Optional list of decorator strings (without @).
            indent: Base indentation level.
        """
        self.name: str = name
        if isinstance(bases, list):
            bases_str: str = ", ".join(bases)
        else:
            bases_str = bases
        self._bases: str = f"({bases_str})" if bases_str else EMPTY_STRING
        self._type_p: str = (
            f"[{', '.join(type_p)}]" if isinstance(type_p, list) else f"[{type_p}]" if type_p else EMPTY_STRING
        )
        self._decorators: str = get_decorators(decorators) if decorators else EMPTY_STRING
        self._docstring: Docstring = Docstring(docstring)
        self._body: BufferHelper = BufferHelper(indent=indent + 1)
        self._added_lines: BufferHelper = BufferHelper(indent=indent + 1)
        self._added_lines.write(body, suffix=NEWLINE) if body else None
        self._result: BufferHelper = BufferHelper()

    @property
    def signature(self) -> str:
        """Set or update the class signature.

        Returns:
            string representing the class signature.
        """
        return f"class {self.name}{self._type_p}{self._bases}{COLON}"

    def render(self) -> str:
        """Render the class to a string.

        Returns:
            The complete class definition as a string.
        """
        if self._decorators:
            self._result.write(self._decorators, suffix=NEWLINE)
        self._result.write(self.signature, suffix=NEWLINE)
        if self._docstring:
            self._body.write(self._docstring.render(), suffix=NEWLINE)
        if self._added_lines.not_empty:
            self._body.write(self._added_lines.getvalue())
            self._result.write(self._body.getvalue())
        else:
            self._body.write(ELLIPSIS)
        self._result.write(self._body.getvalue())
        result: str = self._result.getvalue()
        self.clear()
        return result

    def clear(self) -> Self:
        """Clear the class body and docstring."""
        self.name = EMPTY_STRING
        self._bases = EMPTY_STRING
        self._decorators = EMPTY_STRING
        self._docstring.clear()
        self._body.clear()
        self._result.clear()
        self._added_lines.clear()
        return self


class CodeSection:
    """A code section buffer with indentation management and context managers for code blocks."""

    def __init__(self, name: Sections) -> None:
        """Initialize the CodeSection with a name and empty buffer."""
        self.section_name: str = name
        self._buffer: list[str] = []
        self._current_indent: int = 0

    def add(self, line: str, indent: int = 0) -> None:
        """Add a line to the buffer with the current indentation.

        Args:
            line: The line to add to the buffer.
            indent: Relative indent change (can be negative to outdent).
        """
        self._current_indent += indent
        indented_line: str = INDENT * self._current_indent + line
        self._buffer.append(indented_line)

    def add_blank(self) -> None:
        """Add a blank line to the buffer."""
        self._buffer.append(EMPTY_STRING)

    def set_indent(self, level: int) -> None:
        """Set the absolute indentation level.

        Args:
            level: The indentation level to set (0 = no indent).
        """
        self._current_indent = level

    def reset_indent(self) -> None:
        """Reset indentation to 0."""
        self._current_indent = 0

    def get(self) -> list[str]:
        """Get the current buffer lines.

        Returns:
            A list of strings representing the buffer lines.
        """
        return self._buffer

    @contextmanager
    def block(self, header: str) -> Generator[None, Any]:
        """Context manager for a generic code block with automatic indentation.

        Args:
            header: The header line (will have colon appended if not present).

        Yields:
            None
        """
        header_line: str = header if header.endswith(COLON) else header + COLON
        self.add(header_line)
        self._current_indent += 1
        try:
            yield
        finally:
            self._current_indent -= 1

    @contextmanager
    def function(self, name: str, args: str = EMPTY_STRING, returns: str | None = None) -> Generator[None, Any]:
        """Context manager for a function definition.

        Args:
            name: Function name.
            args: Function arguments (without parentheses).
            returns: Optional return type annotation.

        Yields:
            None
        """
        signature: str = f"def {name}({args})"
        if returns:
            signature += f" -> {returns}"
        with self.block(signature):
            yield

    @contextmanager
    def class_def(self, name: str, bases: str = EMPTY_STRING) -> Generator[None, Any]:
        """Context manager for a class definition.

        Args:
            name: Class name.
            bases: Optional base classes (without parentheses).

        Yields:
            None
        """
        class_line: str = f"class {name}({bases})" if bases else f"class {name}"
        with self.block(class_line):
            yield

    @contextmanager
    def if_block(self, condition: str):
        """Context manager for an if statement.

        Args:
            condition: The condition to test.

        Yields:
            None
        """
        with self.block(f"if {condition}"):
            yield

    @contextmanager
    def elif_block(self, condition: str) -> Generator[None, Any]:
        """Context manager for an elif statement.

        Args:
            condition: The condition to test.

        Yields:
            None
        """
        with self.block(f"elif {condition}"):
            yield

    @contextmanager
    def else_block(self) -> Generator[None, Any]:
        """Context manager for an else statement.

        Yields:
            None
        """
        with self.block("else"):
            yield

    @contextmanager
    def with_block(self, expression: str, as_var: str | None = None) -> Generator[None, Any]:
        """Context manager for a with statement.

        Args:
            expression: The context manager expression.
            as_var: Optional variable name for 'as' clause.

        Yields:
            None
        """
        with_line: str = f"with {expression}"
        if as_var:
            with_line += f" as {as_var}"
        with self.block(with_line):
            yield

    @contextmanager
    def try_block(self) -> Generator[None, Any]:
        """Context manager for a try statement.

        Yields:
            None
        """
        with self.block("try"):
            yield

    @contextmanager
    def except_block(self, exception: str | None = None, as_var: str | None = None) -> Generator[None, Any]:
        """Context manager for an except statement.

        Args:
            exception: Optional exception type to catch.
            as_var: Optional variable name for 'as' clause.

        Yields:
            None
        """
        except_line = "except"
        if exception:
            except_line += f" {exception}"
        if as_var:
            except_line += f" as {as_var}"
        with self.block(except_line):
            yield

    @contextmanager
    def finally_block(self) -> Generator[None, Any]:
        """Context manager for a finally statement.

        Yields:
            None
        """
        with self.block("finally"):
            yield

    @contextmanager
    def for_loop(self, variable: str, iterable: str) -> Generator[None, Any]:
        """Context manager for a for loop.

        Args:
            variable: Loop variable name.
            iterable: Expression to iterate over.

        Yields:
            None
        """
        with self.block(f"for {variable} in {iterable}"):
            yield

    @contextmanager
    def while_loop(self, condition: str) -> Generator[None, Any]:
        """Context manager for a while loop.

        Args:
            condition: The loop condition.

        Yields:
            None
        """
        with self.block(f"while {condition}"):
            yield


class FileBuilder:
    """A file builder that organizes code into logical sections with automatic formatting."""

    def __init__(self) -> None:
        """Initialize the FileBuilder with empty sections."""
        self._sections: dict[Sections, CodeSection] = {
            "header": CodeSection("header"),
            "imports": CodeSection("imports"),
            "type_checking": CodeSection("type_checking"),
            "body": CodeSection("body"),
            "footer": CodeSection("footer"),
        }

    def add(self, section: Sections, line: str, indent: int = 0) -> None:
        """Add a line to the buffer in the specified section.

        Args:
            section: The section where the line should be added.
            line: The line to add to the buffer.
            indent: Relative indent change for this line.
        """
        self._sections[section].add(line, indent)

    def get_section(self, section: Sections) -> CodeSection:
        """Get a specific section buffer for direct manipulation.

        Args:
            section: The section to retrieve.

        Returns:
            The CodeSection for the specified section.
        """
        return self._sections[section]

    def render(self, add_section_separators: bool = False) -> str:
        """Render the buffer into a single string with sections in order.

        Args:
            add_section_separators: If True, add blank lines between non-empty sections.

        Returns:
            A string containing all lines in the buffer, ordered by section.
        """
        output_lines: list[str] = []
        sections_order: tuple[Sections, ...] = ("header", "imports", "type_checking", "body", "footer")

        for section in sections_order:
            code_section: CodeSection = self._sections[section]
            section_lines: list[str] = code_section.get()

            if section_lines:
                if output_lines and add_section_separators:
                    output_lines.append(EMPTY_STRING)
                output_lines.extend(section_lines)

        return "\n".join(output_lines)


if __name__ == "__main__":
    func_builder = FunctionBuilder(
        name="greet",
        args=[Arg(name="name", annotation=str), Arg(name="greeting", annotation=str, default='"Hello"')],
        returns="str",
        docstring="Return a greeting message.",
        body='return f"{greeting}, {name}!"',
    )
    print(func_builder.render())

    cls_builder = ClassBuilder(
        name="Greeter",
        bases=["BaseGreeter"],
        docstring="A simple greeter class.",
    )
    print(cls_builder.render())
