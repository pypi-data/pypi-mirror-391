"""A multiprocessing lock implemented using shared memory and atomics."""

from .lock import SharedMemoryLock
from .mutex import FutexNotSupportedError, SharedMemoryMutex

__version__ = "0.1.2"

__all__ = [
    "SharedMemoryLock",
    "SharedMemoryMutex",
    "FutexNotSupportedError",
]
