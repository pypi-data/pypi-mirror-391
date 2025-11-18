"""A set of helpers for XML file handling."""

from typing import TYPE_CHECKING
from xml.etree.ElementTree import Element, ElementTree

if TYPE_CHECKING:
    Tree = ElementTree[Element]
else:
    Tree = ElementTree


from .file_handler import XMLFilehandler
from .helpers import to_elem

__all__ = [
    "Element",
    "ElementTree",
    "Tree",
    "XMLFilehandler",
    "to_elem",
]
