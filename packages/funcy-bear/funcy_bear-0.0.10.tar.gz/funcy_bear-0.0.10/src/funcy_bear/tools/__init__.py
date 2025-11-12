"""Generally useful tools like data structures, caching, and freezing."""

from .constant import Const
from .currying import Currying
from .dispatcher import Dispatcher
from .freezing import FrozenDict, freeze
from .lru_cache import LRUCache
from .names import Names
from .priority_queue import PriorityQueue
from .simple_queue import SimpooQueue
from .simple_stack import SimpleStack

__all__ = [
    "Const",
    "Currying",
    "Dispatcher",
    "FrozenDict",
    "LRUCache",
    "Names",
    "PriorityQueue",
    "SimpleStack",
    "SimpooQueue",
    "freeze",
]
