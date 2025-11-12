"""A multiprocessing lock implemented using shared memory and atomics."""

from .lock import SharedMemoryLock
from .mutex import FutexNotSupportedError, SharedMemoryMutex

__version__ = "0.1.3"

__all__ = [
    "SharedMemoryLock",
    "SharedMemoryMutex",
    "FutexNotSupportedError",
]
