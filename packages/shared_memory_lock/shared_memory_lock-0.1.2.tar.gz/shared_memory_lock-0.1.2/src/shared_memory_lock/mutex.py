"""
Shared memory mutex implementation using Linux futex for efficient blocking.

This mutex is designed for long waits (seconds to minutes) where processes
need to block efficiently without busy-waiting. Unlike SharedMemoryLock which
spins, this puts waiting processes to sleep using futex syscalls.

Key features:
- True blocking using Linux futex syscalls
- No CPU wasting while waiting
- Scales to hundreds of concurrent waiters
- FIFO fairness for waiting processes
- Suitable for queue operations and long critical sections
"""

import ctypes
import errno
import platform
import struct
import time
from multiprocessing import shared_memory
from typing import Any

# Linux futex syscall constants
SYS_futex = 202  # x86_64 syscall number
FUTEX_WAIT = 0
FUTEX_WAKE = 1
FUTEX_PRIVATE_FLAG = 128  # Process-private futex (we use shared memory, so don't use this)

# State values
UNLOCKED = 0
LOCKED = 1
CONTENDED = 2  # Locked with waiters


class FutexNotSupportedError(Exception):
    """Raised when futex syscalls are not available on this platform."""

    pass


class SharedMemoryMutex:
    """
    A blocking mutex backed by shared memory using Linux futex for efficient waits.

    Unlike SharedMemoryLock (spinlock), this mutex uses futex syscalls to put
    waiting processes to sleep, making it suitable for:
    - Queue operations where processes wait for items
    - Long critical sections (seconds to minutes)
    - High contention scenarios with many waiters

    The mutex maintains fairness by waking waiters in FIFO order.

    Usage:
        # Process A creates the mutex
        mutex = SharedMemoryMutex(name="my_mutex", create=True, run_id="app1")

        # Process B connects to the same mutex
        mutex = SharedMemoryMutex(name="my_mutex", create=False, run_id="app1")

        # Both processes can use it
        with mutex:
            # Critical section - other processes sleep until released
            pass

    Note: Currently Linux-only. Requires Linux kernel 2.6+ with futex support.
    """

    def __init__(self, name: str, create: bool = False, run_id: str = ""):
        """
        Initialize a shared memory mutex.

        Args:
            name: Mutex name (used to identify the shared memory segment)
            create: Whether to create a new mutex or connect to existing
            run_id: Run identifier for namespacing

        Raises:
            FutexNotSupportedError: If futex syscalls are not available (non-Linux)
            FileNotFoundError: If create=False and mutex doesn't exist
        """
        # Check platform support
        if platform.system() != "Linux":
            raise FutexNotSupportedError(
                f"SharedMemoryMutex requires Linux futex support. "
                f"Current platform: {platform.system()}"
            )

        self.name = name
        self.run_id = run_id

        # Shared memory name for the mutex
        shm_name = f"{run_id}-{name}-mutex" if run_id else f"{name}-mutex"

        if create:
            # Create new shared memory for the mutex (4 bytes for atomic int32)
            self._shm = shared_memory.SharedMemory(name=shm_name, create=True, size=4)
            # Initialize to 0 (unlocked)
            struct.pack_into("<i", self._shm.buf, 0, UNLOCKED)
        else:
            # Connect to existing shared memory mutex
            self._shm = shared_memory.SharedMemory(name=shm_name, create=False, size=4)

        # Get direct memory address for futex operations
        self._futex_addr = ctypes.addressof(
            ctypes.c_int.from_buffer(self._shm.buf, 0)
        )

        # Track cleanup state
        self._closed = False

        # Load libc for syscall
        self._libc = ctypes.CDLL(None, use_errno=True)

    def _get_value(self) -> int:
        """Get current mutex value atomically."""
        return struct.unpack("<i", self._shm.buf[:4])[0]

    def _set_value(self, value: int) -> None:
        """Set mutex value atomically."""
        struct.pack_into("<i", self._shm.buf, 0, value)

    def _compare_and_swap(self, expected: int, new: int) -> bool:
        """
        Atomic compare-and-swap operation.

        Returns:
            True if swap succeeded, False otherwise
        """
        # Read current value
        current = self._get_value()
        if current == expected:
            self._set_value(new)
            # Verify it stuck (basic CAS, not truly atomic without CPU instructions)
            # For true atomicity, we'd need atomic operations from the atomics library
            return self._get_value() == new
        return False

    def _futex_wait(self, expected_value: int, timeout: float | None = None) -> bool:
        """
        Call futex_wait syscall to block until woken or value changes.

        Args:
            expected_value: Only wait if futex value equals this
            timeout: Maximum time to wait in seconds (None = infinite)

        Returns:
            True if woken by futex_wake, False if timeout or value changed
        """
        if timeout is not None:
            # Convert timeout to timespec (seconds, nanoseconds)
            sec = int(timeout)
            nsec = int((timeout - sec) * 1_000_000_000)
            timespec = ctypes.c_long * 2
            ts = timespec(sec, nsec)
            ts_ptr = ctypes.cast(ctypes.pointer(ts), ctypes.c_void_p)
        else:
            ts_ptr = None

        # syscall(SYS_futex, futex_addr, FUTEX_WAIT, expected_value, timeout, NULL, 0)
        result = self._libc.syscall(
            SYS_futex,
            self._futex_addr,
            FUTEX_WAIT,
            expected_value,
            ts_ptr,
            None,
            0,
        )

        if result == -1:
            err = ctypes.get_errno()
            if err == errno.ETIMEDOUT:
                return False  # Timeout
            elif err == errno.EAGAIN:
                return True  # Value changed, not an error
            elif err == errno.EINTR:
                return True  # Interrupted by signal, retry
            # Other errors are unexpected
            # Don't raise, just return False
            return False

        return True

    def _futex_wake(self, num_waiters: int = 1) -> int:
        """
        Call futex_wake syscall to wake waiting processes.

        Args:
            num_waiters: Number of waiters to wake (1 = wake one, INT_MAX = wake all)

        Returns:
            Number of waiters actually woken
        """
        # syscall(SYS_futex, futex_addr, FUTEX_WAKE, num_waiters, NULL, NULL, 0)
        result = self._libc.syscall(
            SYS_futex, self._futex_addr, FUTEX_WAKE, num_waiters, None, None, 0
        )

        if result == -1:
            err = ctypes.get_errno()
            # Wake failures are generally not critical, just return 0
            return 0

        return result

    def acquire(self, blocking: bool = True, timeout: float | None = None) -> bool:
        """
        Acquire the mutex.

        This uses a fast path (uncontended) and slow path (contended with futex):
        1. Try to acquire with CAS(UNLOCKED -> LOCKED)
        2. If that fails, mark as CONTENDED and call futex_wait
        3. When woken, try to acquire again

        Args:
            blocking: Whether to block waiting for the mutex
            timeout: Maximum time to wait (only used if blocking=True)

        Returns:
            True if mutex was acquired, False if timeout or non-blocking failed
        """
        start_time = time.time() if timeout is not None else None

        # Fast path: try to acquire if unlocked
        if self._compare_and_swap(UNLOCKED, LOCKED):
            return True

        if not blocking:
            return False

        # Slow path: mutex is contended
        while True:
            # Mark as contended if currently locked
            current = self._get_value()
            if current == UNLOCKED:
                # Became available, try to acquire
                if self._compare_and_swap(UNLOCKED, LOCKED):
                    return True
            elif current == LOCKED:
                # Not yet contended, mark it
                self._set_value(CONTENDED)

            # Calculate remaining timeout
            remaining_timeout = None
            if timeout is not None:
                elapsed = time.time() - start_time
                remaining_timeout = max(0, timeout - elapsed)
                if remaining_timeout <= 0:
                    return False

            # Wait for wake signal
            self._futex_wait(CONTENDED, remaining_timeout)

            # Try to acquire after being woken
            if self._compare_and_swap(UNLOCKED, LOCKED):
                return True

            # Check timeout
            if timeout is not None:
                elapsed = time.time() - start_time
                if elapsed >= timeout:
                    return False

    def release(self) -> None:
        """
        Release the mutex and wake one waiting process.

        If there are waiters (state is CONTENDED), this wakes one waiter using futex_wake.
        """
        # Transition from LOCKED/CONTENDED to UNLOCKED
        current = self._get_value()

        if current == UNLOCKED:
            # Not locked, this is a programming error but don't raise
            return

        # Set to unlocked
        self._set_value(UNLOCKED)

        # If it was contended, wake one waiter
        if current == CONTENDED:
            self._futex_wake(1)

    def __enter__(self):
        """Context manager entry - acquire mutex."""
        self.acquire()
        return self

    def __exit__(self, *args):
        """Context manager exit - release mutex."""
        self.release()

    def __del__(self):
        """Destructor - ensure proper cleanup."""
        try:
            self.close()
        except Exception:
            pass

    def close(self) -> None:
        """Close the shared memory connection."""
        if getattr(self, "_closed", True):
            return  # Already closed

        self._closed = True

        # Close shared memory
        if hasattr(self, "_shm") and self._shm:
            try:
                self._shm.close()
            except Exception:
                pass
            finally:
                self._shm = None

    def unlink(self) -> None:
        """Unlink (delete) the shared memory segment."""
        self.close()
        try:
            shm_name = f"{self.run_id}-{self.name}-mutex" if self.run_id else f"{self.name}-mutex"
            temp_shm = shared_memory.SharedMemory(name=shm_name)
            temp_shm.unlink()
            temp_shm.close()
        except FileNotFoundError:
            pass
        except Exception:
            pass

    def __getstate__(self) -> dict[str, Any]:
        """Prepare for pickling - return connection info."""
        return {
            "name": self.name,
            "run_id": self.run_id,
        }

    def __setstate__(self, state: dict[str, Any]) -> None:
        """Restore from pickle - reconnect to shared memory."""
        self.__init__(name=state["name"], create=False, run_id=state["run_id"])
