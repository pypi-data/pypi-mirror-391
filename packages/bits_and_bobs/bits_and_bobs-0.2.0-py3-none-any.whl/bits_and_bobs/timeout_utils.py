"""Functions related to timeout handling."""

import signal
from types import FrameType, TracebackType


class timeout:
    """Timeout context manager.

    This uses the `signal` module to raise a `TimeoutError` if the code inside the
    context manager takes longer than the specified number of seconds to execute.

    Example:
        >>> import time
        >>> try:
        ...     with timeout(seconds=1, error_message="This is a timeout!"):
        ...         time.sleep(2)
        ... except TimeoutError as e:
        ...     print(e)
        This is a timeout!
    """

    def __init__(self, seconds: int, error_message: str) -> None:
        """Initialise the context manager.

        Args:
            seconds:
                The number of seconds before the timeout.
            error_message:
                The error message to raise when the timeout occurs.
        """
        self.seconds = seconds
        self.error_message = error_message

    def handle_timeout(self, signum: int, frame: int | FrameType | None) -> None:
        """Handle the timeout.

        Args:
            signum:
                The signal number.
            frame:
                The frame.

        Raises:
            TimeoutError:
                The error message.
        """
        raise TimeoutError(self.error_message)

    def __enter__(self) -> None:
        """Enter the context manager.

        This will raise a `SIGALRM` signal after `self.seconds` seconds, and we handle
        this signal by calling the `handle_timeout` method.
        """
        signal.signal(signalnum=signal.SIGALRM, handler=self.handle_timeout)
        signal.alarm(self.seconds)

    def __exit__(
        self,
        type: type[BaseException] | None,
        value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """Exit the context manager.

        This will disable the alarm.

        Args:
            type:
                The type of the exception.
            value:
                The value of the exception.
            traceback:
                The traceback of the exception.
        """
        signal.alarm(0)
