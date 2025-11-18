"""Utility functions."""

# pylint: disable=protected-access
import logging
import re
import typing as t

from fw_client import FWClient

log = logging.getLogger(__name__)

if t.TYPE_CHECKING:  # pragma: no cover
    from flywheel import Client

HIERARCHY = ["group", "project", "subject", "session", "acquisition"]
SDK_HOST_RE = re.compile(r"(\w+):\/\/(\S+):(\d+)(\/api)?")


def paginate(fw: FWClient, baseurl: str, filter_param: str = "") -> t.Iterator[t.Any]:
    """Helper to paginate over filter endpoints."""
    params = {"limit": 100, "after_id": None, "filter": filter_param}
    while True:
        results = fw.get(baseurl, params=params)
        if "results" in results:  # type: ignore
            results = results["results"]  # type: ignore
        if not results:
            break
        for item in results:
            yield item
        params["after_id"] = results[-1]._id  # type: ignore


def add_ctype(iterator: t.Iterable[t.Any], c_type: str) -> t.Iterator[t.Any]:
    """Add container type to an iterable of containers.

    Args:
        iterator (t.Iterable[t.Any]): Iterable of containers.
        c_type (str): Container type to add

    Yields:
        Iterator[t.Any]: Iterable of containers with container_type attribute
    """
    for it in iterator:
        setattr(it, "container_type", c_type)
        yield it


def get_container_type(container: t.Any) -> str:
    """Return container type of a given container.

    We don't have a `container_type` attribute on some non-SDK responses, so we
    need another way to determine container type.
    """
    if hasattr(container, "container_type"):
        return container.container_type
    # Unique attributes to files and analyses
    if "file_id" in container:
        return "file"
    if "inputs" in container:  # pragma: no cover
        return "analysis"
    hierarchy_r = list(reversed(HIERARCHY))
    # Check based on existence of parents starting at session
    for i, parent in enumerate(hierarchy_r[1:]):
        if container.parents.get(parent):
            return hierarchy_r[i]
    raise RuntimeError(  # pragma: no cover
        f"Could not determine container type of container: {container._id}"
    )


def reload_file_parent(
    client: "Client",
    file: t.Any,
) -> t.Any:
    """Populate _parent attribute on SDK files."""
    if getattr(file, "parent", None) is not None:
        return file
    get_parent_fn = getattr(client, f"get_{file.parent_ref.type}")
    file._parent = get_parent_fn(file.parent_ref.id)
    return file


def get_api_key_from_container(container: t.Any) -> t.Optional[str]:
    """Parse API-key from SDK container object."""
    try:
        api_context = getattr(container, "_ContainerBase__context")
        sdk_config = api_context.api_client.configuration
        match = SDK_HOST_RE.match(sdk_config.host)
        if match is None:
            raise ValueError(f"Invalid host format: {sdk_config.host}")
        match_groups = match.groups()  # type: ignore
        host = f"{match_groups[0] or 'https'}://{match_groups[1]}:{match_groups[2]}"
        key = sdk_config.api_key["Authorization"]
        return f"{host}:{key}"
    except AttributeError:
        log.debug("AttributeError when getting api key", exc_info=True)
        return None
