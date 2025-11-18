"""A collection of generally useful protocols."""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class FrozenClass(Protocol):
    """A protocol for frozen (immutable) classes."""

    __frozen__: bool


@runtime_checkable
class Bindable(Protocol):
    """A protocol for objects that can bind documents."""

    def bind(self, doc: Any, **kwargs) -> None:
        """Bind a document to the object."""

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        """Call the object with the given arguments."""


@runtime_checkable
class CollectionProtocol(Protocol):
    """A protocol for collections that support len() and indexing."""

    def __len__(self) -> int: ...
    def __getitem__(self, index: int) -> Any: ...
    def __setitem__(self, index: int, value: Any) -> None: ...
    def pop(self) -> Any: ...  # noqa: D102
    def remove(self, item: Any) -> None: ...  # noqa: D102
    def get(self, index: int) -> Any: ...  # noqa: D102
    def copy(self) -> Any: ...  # noqa: D102
    def clear(self) -> None: ...  # noqa: D102
    def join(self, d: str) -> str: ...  # noqa: D102


class FileHandlerProtocol[T](Protocol):
    """Basic protocol for file handlers."""

    def read(self, **kwargs) -> T:
        """Return parsed records from the file (format-specific in subclass)."""
        raise NotImplementedError

    def write(self, data: T, **kwargs) -> None:
        """Replace file contents with `data` (format-specific in subclass)."""
        raise NotImplementedError

    def clear(self) -> None:
        """Clear the file contents using an exclusive lock."""
        raise NotImplementedError

    @property
    def closed(self) -> bool:
        """Check if the file handle is closed."""
        raise NotImplementedError

    def close(self) -> None:
        """Close the file handle if open."""
        raise NotImplementedError

    def flush(self) -> None:
        """Flush the file handle if open."""
        raise NotImplementedError
