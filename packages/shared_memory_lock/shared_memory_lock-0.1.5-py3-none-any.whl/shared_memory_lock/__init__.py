"""A multiprocessing lock implemented using shared memory and atomics."""

from .lock import SharedMemoryLock
from .mutex import SharedMemoryMutex

__version__ = "0.1.5"

__all__ = [
    "SharedMemoryLock",
    "SharedMemoryMutex",
]
