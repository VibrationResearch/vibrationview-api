"""
COM Worker Thread

Provides a dedicated thread for all COM interactions, ensuring proper
COM apartment threading. All COM calls are submitted as callables to a
queue and executed on the worker thread.
"""

import pythoncom
import threading
import queue
from concurrent.futures import Future
from functools import wraps


class COMWorkerThread:
    """A dedicated thread that owns the COM object and processes all COM calls.

    All COM interactions are submitted as callables to a queue and executed
    on this thread, ensuring proper COM apartment threading.
    """

    def __init__(self):
        self._queue = queue.Queue()
        self._thread = None
        self._thread_id = None
        self._started = threading.Event()
        self._lock = threading.Lock()

    def start(self):
        """Start the worker thread if not already running."""
        with self._lock:
            if self._thread is not None and self._thread.is_alive():
                return
            self._started.clear()
            self._thread = threading.Thread(target=self._run, daemon=True, name="COMWorkerThread")
            self._thread.start()
            self._started.wait()

    def stop(self):
        """Signal the worker thread to stop and wait for it to finish."""
        with self._lock:
            if self._thread is None or not self._thread.is_alive():
                return
        self._queue.put(None)  # sentinel
        self._thread.join(timeout=10)

    @property
    def is_alive(self):
        return self._thread is not None and self._thread.is_alive()

    @property
    def on_worker_thread(self):
        """True if the caller is on the COM worker thread."""
        return threading.get_ident() == self._thread_id

    def submit(self, fn, *args, **kwargs):
        """Submit a callable to run on the COM thread. Returns a Future.

        If called from the worker thread itself (re-entrant call), executes
        the callable directly to avoid deadlock.
        """
        if self.on_worker_thread:
            # Already on the worker thread — execute directly
            future = Future()
            future.set_running_or_notify_cancel()
            try:
                result = fn(*args, **kwargs)
                future.set_result(result)
            except BaseException as exc:
                future.set_exception(exc)
            return future

        if not self.is_alive:
            raise RuntimeError("COM worker thread is not running")
        future = Future()
        self._queue.put((future, fn, args, kwargs))
        return future

    def _run(self):
        """Worker loop: initialize COM, then process queued callables."""
        self._thread_id = threading.get_ident()
        pythoncom.CoInitialize()
        try:
            self._started.set()
            while True:
                item = self._queue.get()
                if item is None:
                    break  # shutdown sentinel
                future, fn, args, kwargs = item
                if future.set_running_or_notify_cancel():
                    try:
                        result = fn(*args, **kwargs)
                        future.set_result(result)
                    except BaseException as exc:
                        future.set_exception(exc)
        finally:
            pythoncom.CoUninitialize()


# Module-level shared worker thread
_com_worker = COMWorkerThread()
_com_worker_lock = threading.Lock()


def _ensure_worker():
    """Ensure the shared COM worker thread is running."""
    if not _com_worker.is_alive:
        with _com_worker_lock:
            if not _com_worker.is_alive:
                _com_worker.start()


def com_method(func):
    """Decorator that marshals COM method calls to the worker thread."""
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        _ensure_worker()

        # Define an inner helper function that executes ENTIRELY on the background thread
        def _execute_on_thread():
            # Check and create the object strictly on the COM thread context
            if getattr(self, '_vv_object', None) is None:
                self._create_com_object()
            return func(self, *args, **kwargs)

        # Submit the helper function instead of the raw function
        future = _com_worker.submit(_execute_on_thread)
        return future.result()

    return wrapper
