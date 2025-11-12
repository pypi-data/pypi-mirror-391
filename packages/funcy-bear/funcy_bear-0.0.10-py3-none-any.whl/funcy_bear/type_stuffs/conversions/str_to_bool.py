"""Convert string representations of types to actual Python types in various ways."""

from warnings import deprecated

POSSIBLE_BOOL_STRINGS: tuple[str, ...] = ("true", "false", "1", "0", "yes", "no")
POSSIBLE_BOOL_VALUES: tuple[str, ...] = ("true", "1", "yes")


def parse_bool(val: str) -> bool:
    """Convert a string representation of a boolean to an actual boolean value.

    Returns:
        bool: The boolean value.
    """
    return str(val).strip().lower() in POSSIBLE_BOOL_VALUES


@deprecated("Use parse_bool instead.")
def str_to_bool(val: str) -> bool:
    """[DEPRECATED] Use parse_bool instead."""
    return parse_bool(val)
