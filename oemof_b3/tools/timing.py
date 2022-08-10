r"""
A Timer class, adapted from https://github.com/realpython/codetiming
"""
import datetime
import time


class Timer:
    def __init__(self, text, logger=print):
        self._start_time = None
        self.text = text
        self.logger = logger

    def start(self):
        """Start a new timer"""
        self._start_time = time.perf_counter()

    def stop(self):
        """Stop the timer, and report the elapsed time"""
        elapsed_time = time.perf_counter() - self._start_time
        self._start_time = None
        if self.logger:
            self.logger(
                self.text + f" Elapsed time: {datetime.timedelta(seconds=elapsed_time)}"
            )

    def __enter__(self):
        """Start a new timer as a context manager"""
        self.start()
        return self

    def __exit__(self, *exc_info):
        """Stop the context manager timer"""
        self.stop()
