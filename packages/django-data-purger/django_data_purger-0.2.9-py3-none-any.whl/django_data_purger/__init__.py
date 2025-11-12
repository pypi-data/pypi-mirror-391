"""Periodically remove data from your Django app."""

from importlib.metadata import PackageNotFoundError, version

from .context import data_purger_is_running
from .data_purger import DataPurger, PurgeDeleteResult, PurgeResult, PurgeUpdateResult
from .enums import DataPurgerAction
from .exceptions import DataPurgerException
from .services import (
    get_tables_with_data_purging_enabled,
    run_data_purger,
    run_data_purgers,
)

try:
    __version__ = version(__name__)
except PackageNotFoundError:  # pragma: no cover
    __version__ = "unknown"


__all__ = [
    "DataPurger",
    "DataPurgerAction",
    "DataPurgerException",
    "PurgeDeleteResult",
    "PurgeResult",
    "PurgeUpdateResult",
    "data_purger_is_running",
    "get_tables_with_data_purging_enabled",
    "run_data_purger",
    "run_data_purgers",
]
