"""Package init module."""

try:
    from importlib.metadata import version
except ImportError:  # pragma: no cover
    from importlib_metadata import version  # type: ignore

PKG_NAME = __name__
__version__ = version(PKG_NAME)

from .config import (  # noqa: E402
    CurationConfig,
    DefaultLogRecord,
    ReporterConfig,
    WalkerConfig,
)
from .curator import FileCurator, HierarchyCurator  # noqa: E402
from .reporters import AggregatedReporter  # noqa: E402
from .walker import Walker  # noqa: E402

__all__ = [
    "HierarchyCurator",
    "FileCurator",
    "Walker",
    "AggregatedReporter",
    "DefaultLogRecord",
    "CurationConfig",
    "WalkerConfig",
    "ReporterConfig",
]
