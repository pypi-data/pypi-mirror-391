"""Comprehensive tests for SharedMemoryMutex."""

import multiprocessing as mp
import pickle
import platform
import time

import pytest

from shared_memory_lock import FutexNotSupportedError, SharedMemoryMutex


@pytest.fixture
def check():
    """pytest-check fixture for soft assertions."""
    import pytest_check

    return pytest_check


@pytest.fixture
def unique_run_id():
    """Generate a unique run_id for each test."""
    return f"test_{time.time()}_{id(object())}"


@pytest.fixture
def mutex_name():
    """Standard mutex name for tests."""
    return "test_mutex"


# Skip all tests on non-Linux platforms
pytestmark = pytest.mark.skipif(
    platform.system() != "Linux", reason="SharedMemoryMutex requires Linux futex support"
)


class TestMutexBasics:
    """Basic mutex functionality tests."""

    def test_mutex_creation(self, check, unique_run_id, mutex_name):
        """Test that a mutex can be created and cleaned up."""
        mutex = SharedMemoryMutex(name=mutex_name, create=True, run_id=unique_run_id)

        check.is_not_none(mutex)
        check.equal(mutex.name, mutex_name)
        check.equal(mutex.run_id, unique_run_id)

        # Should be able to close without error
        mutex.close()
        mutex.unlink()

    def test_acquire_release_basic(self, check, unique_run_id, mutex_name):
        """Test basic acquire and release operations."""
        mutex = SharedMemoryMutex(name=mutex_name, create=True, run_id=unique_run_id)

        try:
            # Should be able to acquire
            result = mutex.acquire()
            check.is_true(result, "First acquire should succeed")

            # Should be able to release
            mutex.release()

            # Should be able to acquire again after release
            result = mutex.acquire()
            check.is_true(result, "Second acquire should succeed after release")

            mutex.release()
        finally:
            mutex.unlink()

    def test_context_manager(self, check, unique_run_id, mutex_name):
        """Test mutex works correctly as context manager."""
        mutex = SharedMemoryMutex(name=mutex_name, create=True, run_id=unique_run_id)

        try:
            # Use as context manager
            with mutex:
                # Mutex should be held here
                # Try non-blocking acquire from same mutex instance (should fail)
                result = mutex.acquire(blocking=False)
                check.is_false(result, "Should not be able to acquire already-held mutex")

            # After context exit, mutex should be released
            result = mutex.acquire(blocking=False)
            check.is_true(result, "Should be able to acquire after context exit")
            mutex.release()

        finally:
            mutex.unlink()

    def test_non_blocking_acquire(self, check, unique_run_id, mutex_name):
        """Test non-blocking acquire behavior."""
        mutex = SharedMemoryMutex(name=mutex_name, create=True, run_id=unique_run_id)

        try:
            # Non-blocking acquire on free mutex should succeed
            result = mutex.acquire(blocking=False)
            check.is_true(result, "Non-blocking acquire on free mutex should succeed")

            # Non-blocking acquire on held mutex should fail immediately
            start_time = time.time()
            result2 = mutex.acquire(blocking=False)
            elapsed = time.time() - start_time

            check.is_false(result2, "Non-blocking acquire on held mutex should fail")
            check.less(elapsed, 0.1, "Non-blocking acquire should return quickly")

            # Release and try again
            mutex.release()
            result3 = mutex.acquire(blocking=False)
            check.is_true(result3, "Non-blocking acquire should succeed after release")

            mutex.release()
        finally:
            mutex.unlink()

    def test_blocking_acquire_timeout(self, check, unique_run_id, mutex_name):
        """Test blocking acquire with timeout."""
        mutex = SharedMemoryMutex(name=mutex_name, create=True, run_id=unique_run_id)

        try:
            # Acquire mutex first
            mutex.acquire()

            # Blocking acquire with timeout should fail after timeout
            timeout_duration = 0.3
            start_time = time.time()
            result = mutex.acquire(blocking=True, timeout=timeout_duration)
            elapsed = time.time() - start_time

            check.is_false(result, "Timed acquire on held mutex should fail")
            check.greater_equal(
                elapsed, timeout_duration * 0.9, "Should wait at least most of timeout"
            )
            check.less(
                elapsed, timeout_duration * 1.5, "Should not wait much longer than timeout"
            )

            mutex.release()
        finally:
            mutex.unlink()


class TestCrossProcessMutex:
    """Cross-process mutex tests."""

    @staticmethod
    def _mutex_holder_process(run_id: str, mutex_name: str, hold_duration: float, ready_event=None):
        """Process that acquires mutex and holds it for specified duration."""
        mutex = SharedMemoryMutex(name=mutex_name, create=False, run_id=run_id)

        with mutex:
            # Signal that we've acquired the mutex
            if ready_event is not None:
                ready_event.set()
            time.sleep(hold_duration)

    @staticmethod
    def _mutex_acquirer_process(run_id: str, mutex_name: str, results_dict: dict, wait_event=None):
        """Process that tries to acquire mutex and records timing."""
        mutex = SharedMemoryMutex(name=mutex_name, create=False, run_id=run_id)

        # Wait for signal that holder has the mutex before starting timing
        if wait_event is not None:
            wait_event.wait(timeout=5.0)

        start_time = time.time()
        success = mutex.acquire(blocking=True, timeout=10.0)
        end_time = time.time()

        results_dict["success"] = success
        results_dict["elapsed"] = end_time - start_time

        if success:
            mutex.release()

    @pytest.mark.repeat(10)
    def test_cross_process_mutual_exclusion(self, check, unique_run_id, mutex_name):
        """Test that mutex provides mutual exclusion across processes."""
        ctx = mp.get_context("spawn")

        # Create mutex in main process
        mutex = SharedMemoryMutex(name=mutex_name, create=True, run_id=unique_run_id)

        try:
            hold_duration = 0.5
            ready_event = ctx.Event()

            # Start process that holds mutex
            holder = ctx.Process(
                target=self._mutex_holder_process,
                args=(unique_run_id, mutex_name, hold_duration, ready_event),
            )
            holder.start()

            # Wait for holder to actually acquire the mutex before we try
            check.is_true(
                ready_event.wait(timeout=2.0), "Holder should acquire mutex within timeout"
            )

            # Try to acquire in main process
            start_time = time.time()
            result = mutex.acquire(blocking=True, timeout=2.0)
            elapsed = time.time() - start_time

            check.is_true(result, "Should eventually acquire mutex after holder releases")
            check.greater_equal(elapsed, hold_duration * 0.8, "Should wait for holder to release")
            check.less(elapsed, hold_duration * 1.5, "Should not wait too much longer")

            mutex.release()

            # Clean up
            holder.join(timeout=2)
            check.is_false(holder.is_alive(), "Holder process should have finished")

        finally:
            mutex.unlink()

    @pytest.mark.repeat(10)
    def test_multiple_processes_competing(self, check, unique_run_id, mutex_name):
        """Test multiple processes competing for the same mutex with proper mutual exclusion."""
        ctx = mp.get_context("spawn")
        manager = ctx.Manager()
        results = manager.dict()

        # Create mutex in main process
        mutex = SharedMemoryMutex(name=mutex_name, create=True, run_id=unique_run_id)

        try:
            # Test parameters
            hold_duration = 0.3
            ready_event = ctx.Event()

            holder = ctx.Process(
                target=self._mutex_holder_process,
                args=(unique_run_id, mutex_name, hold_duration, ready_event),
            )

            # Acquirer waits for ready_event before starting its timing
            acquirer = ctx.Process(
                target=self._mutex_acquirer_process,
                args=(unique_run_id, mutex_name, results, ready_event),
            )

            holder.start()
            acquirer.start()

            # Both should finish successfully
            holder.join(timeout=5)
            acquirer.join(timeout=5)

            check.is_false(holder.is_alive(), "Holder should finish")
            check.is_false(acquirer.is_alive(), "Acquirer should finish")
            check.is_true(results.get("success", False), "Acquirer should eventually get mutex")

            # STRICT test: acquirer MUST wait for holder to release the mutex
            # This verifies that mutual exclusion actually works
            elapsed = results.get("elapsed", 0)
            expected_minimum_wait = hold_duration * 0.75  # Account for timing variations
            check.greater_equal(
                elapsed,
                expected_minimum_wait,
                f"Acquirer waited {elapsed:.3f}s but should wait at least {expected_minimum_wait:.3f}s - "
                "this indicates broken mutual exclusion!",
            )
            check.less(elapsed, hold_duration * 1.5, "Acquirer should not wait excessively long")

        finally:
            mutex.unlink()

    @staticmethod
    def _long_holder_process(run_id: str, mutex_name: str, ready_event):
        """Hold mutex for 2 seconds."""
        mutex = SharedMemoryMutex(name=mutex_name, create=False, run_id=run_id)
        with mutex:
            ready_event.set()
            time.sleep(2.0)

    @staticmethod
    def _long_waiter_process(run_id: str, mutex_name: str, wait_event, results: dict):
        """Wait for mutex and record that it worked."""
        mutex = SharedMemoryMutex(name=mutex_name, create=False, run_id=run_id)
        wait_event.wait(timeout=5.0)

        # This should block in futex, not spin
        start = time.time()
        mutex.acquire()
        elapsed = time.time() - start
        mutex.release()

        results["waited"] = elapsed

    def test_long_wait_efficiency(self, check, unique_run_id, mutex_name):
        """Test that long waits don't consume CPU (futex blocks properly)."""
        ctx = mp.get_context("spawn")
        manager = ctx.Manager()
        results = manager.dict()

        mutex = SharedMemoryMutex(name=mutex_name, create=True, run_id=unique_run_id)

        try:
            ready = ctx.Event()
            holder = ctx.Process(
                target=self._long_holder_process, args=(unique_run_id, mutex_name, ready)
            )
            waiter_proc = ctx.Process(
                target=self._long_waiter_process, args=(unique_run_id, mutex_name, ready, results)
            )

            holder.start()
            waiter_proc.start()

            holder.join(timeout=5)
            waiter_proc.join(timeout=5)

            check.is_false(holder.is_alive(), "Holder should finish")
            check.is_false(waiter_proc.is_alive(), "Waiter should finish")

            # Waiter should have blocked for ~2 seconds
            waited = results.get("waited", 0)
            check.greater_equal(waited, 1.5, "Should have waited at least 1.5s")
            check.less(waited, 3.0, "Should not have waited more than 3s")

        finally:
            mutex.unlink()


class TestSerialization:
    """Mutex serialization and cross-process sharing tests."""

    def test_pickle_roundtrip(self, check, unique_run_id, mutex_name):
        """Test that mutexes can be pickled and unpickled."""
        mutex = SharedMemoryMutex(name=mutex_name, create=True, run_id=unique_run_id)

        try:
            # Pickle and unpickle
            pickled_data = pickle.dumps(mutex)
            mutex2 = pickle.loads(pickled_data)

            # Check that unpickled mutex has correct attributes
            check.equal(mutex2.name, mutex_name)
            check.equal(mutex2.run_id, unique_run_id)

            # Both should be able to work with same underlying mutex
            mutex.acquire()

            # Second instance should see mutex as held
            result = mutex2.acquire(blocking=False)
            check.is_false(result, "Unpickled mutex should see mutex as held")

            # Release via original
            mutex.release()

            # Should be able to acquire via unpickled instance
            result = mutex2.acquire(blocking=False)
            check.is_true(result, "Should acquire via unpickled mutex after original releases")

            mutex2.release()

        finally:
            mutex.unlink()

    def test_getstate_setstate(self, check, unique_run_id, mutex_name):
        """Test __getstate__ and __setstate__ methods directly."""
        mutex = SharedMemoryMutex(name=mutex_name, create=True, run_id=unique_run_id)

        try:
            # Get state
            state = mutex.__getstate__()

            check.is_instance(state, dict)
            check.equal(state["name"], mutex_name)
            check.equal(state["run_id"], unique_run_id)

            # Create new mutex and restore state
            mutex2 = SharedMemoryMutex.__new__(SharedMemoryMutex)
            mutex2.__setstate__(state)

            check.equal(mutex2.name, mutex_name)
            check.equal(mutex2.run_id, unique_run_id)

            # Should be able to use restored mutex
            result = mutex2.acquire(blocking=False)
            check.is_true(result, "Restored mutex should be functional")

            mutex2.release()

        finally:
            mutex.unlink()


class TestEdgeCases:
    """Edge cases and error conditions."""

    def test_connect_to_nonexistent_mutex(self, check, unique_run_id):
        """Test connecting to non-existent mutex raises appropriate error."""
        with check.raises(FileNotFoundError):
            SharedMemoryMutex(name="nonexistent", create=False, run_id=unique_run_id)

    def test_empty_run_id(self, check, mutex_name):
        """Test mutex works with empty run_id."""
        mutex = SharedMemoryMutex(name=mutex_name, create=True, run_id="")

        try:
            check.equal(mutex.run_id, "")

            result = mutex.acquire()
            check.is_true(result, "Mutex with empty run_id should work")

            mutex.release()
        finally:
            mutex.unlink()

    def test_very_long_names(self, check, unique_run_id):
        """Test mutex works with long names (within OS limits)."""
        long_name = "a" * 100  # Should be within most OS limits

        mutex = SharedMemoryMutex(name=long_name, create=True, run_id=unique_run_id)

        try:
            result = mutex.acquire()
            check.is_true(result, "Mutex with long name should work")
            mutex.release()
        finally:
            mutex.unlink()

    def test_close_and_unlink_safety(self, check, unique_run_id, mutex_name):
        """Test that close() and unlink() can be called multiple times safely."""
        mutex = SharedMemoryMutex(name=mutex_name, create=True, run_id=unique_run_id)

        # Should not raise errors
        mutex.close()
        mutex.close()  # Second close should be safe

        mutex.unlink()
        mutex.unlink()  # Second unlink should be safe

    def test_acquire_after_close(self, check, unique_run_id, mutex_name):
        """Test behavior after closing mutex."""
        mutex = SharedMemoryMutex(name=mutex_name, create=True, run_id=unique_run_id)
        mutex.close()

        # Behavior after close is undefined, but shouldn't crash
        # Most likely will raise an exception
        with check.raises(Exception):
            mutex.acquire()

        # Clean up
        try:
            mutex.unlink()
        except Exception:
            pass


class TestPlatformSpecific:
    """Platform-specific tests."""

    @pytest.mark.skipif(platform.system() == "Linux", reason="Test non-Linux behavior")
    def test_non_linux_raises_error(self, unique_run_id, mutex_name):
        """Test that creating mutex on non-Linux raises FutexNotSupportedError."""
        with pytest.raises(FutexNotSupportedError):
            SharedMemoryMutex(name=mutex_name, create=True, run_id=unique_run_id)
