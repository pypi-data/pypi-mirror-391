import contextlib
from contextvars import ContextVar
from typing import Iterator

_data_purger_is_running: ContextVar[bool] = ContextVar(
    "data_purger_is_running", default=False
)


def data_purger_is_running() -> bool:
    """
    Returns True if the data purger is running.
    """

    return _data_purger_is_running.get()


@contextlib.contextmanager
def _activate_data_purger_context() -> Iterator[None]:
    prev_in_bravo_token = _data_purger_is_running.set(True)
    try:
        yield
    finally:
        _data_purger_is_running.reset(prev_in_bravo_token)
