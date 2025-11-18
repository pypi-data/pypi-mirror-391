"""Curation configuration module."""

from pathlib import Path
from typing import Any, Callable, Optional, Type

from pydantic import BaseModel
from pydantic_settings import BaseSettings


class DefaultLogRecord(BaseModel):
    """Default log record.

    Args:
        container_type (str, optional): Container type. Defaults to "".
        container_id (str, optional): Container id. Defaults to "".
        label (str, optional): Container label. Defaults to "".
        err (str, optional): Error message. Defaults to "".
        msg (str, optional): Other message. Defaults to "".
        resolved (bool, optional): Resolved or not. Defaults to False.
    """

    container_type: str = ""
    container_id: str = ""
    label: str = ""
    err: str = ""
    msg: str = ""
    resolved: bool = False

    model_config = {"extra": "ignore"}


class WalkerConfig(BaseSettings):
    """Configuration object for Walker.

    Args:
        depth_first (bool): Walk depth-first (True) or breadth-first (False).
            Default True (depth-first)
        reload (bool): Reload containers when walking. Default True
        stop_level (str): Stop after this level in hierarchy
            (don't queue children).  Default None
        callback (Callable[[Any], bool]): Callback to filter walker.
        exclude_analyses (bool): Exclude analyses when walking. Default False
        exclude_files (bool): Exclude files when walking. Default False
        deserialize (bool): Deserialize containers into SDK models.
        subject_warn_limit (int, default 1000): If starting at project level, this
            is the number of subjects over which there will be a warning for slower
            runtime.
    """

    depth_first: bool = True
    reload: bool = True
    stop_level: Optional[str] = None
    callback: Optional[Callable[[Any], bool]] = None
    exclude_analyses: bool = False
    exclude_files: bool = False
    deserialize: bool = False
    subject_warn_limit: int = 1000

    model_config = {"env_prefix": "FW_CURATION_"}


class ReporterConfig(BaseSettings):
    """Configuration for the Reporter.

    Args:
        report (bool): Turn on aggregated reporting.
        format (Type[BaseModel]): Log report format.
        path: (Path): Output path for report file.
    """

    report: bool = False
    format: Type[BaseModel] = DefaultLogRecord
    path: Path = Path("output/output.csv")

    model_config = {"env_prefix": "FW_CURATION_"}


class CurationConfig(WalkerConfig, ReporterConfig):
    """Class to hold curation config options.

    Args:
        workers (int): Number of worker processes. Default 0.
            If greater than zero, enables multiprocessing on Walker
            and Reporters as well.
    """

    workers: int = 0

    model_config = {"env_prefix": "FW_CURATION_"}
