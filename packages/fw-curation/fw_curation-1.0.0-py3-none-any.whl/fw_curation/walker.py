"""Hierarchy Walker."""

import importlib
import logging
import typing as t
from collections import deque
from collections.abc import Sequence
from multiprocessing import Process
from multiprocessing.managers import SyncManager
from queue import Queue
from threading import Event
from typing import Any, Callable, Iterator, Optional, Tuple

from fw_client import FWClient
from fw_utils import pluralize

from . import PKG_NAME, __version__
from .config import WalkerConfig
from .utils import (
    HIERARCHY,
    add_ctype,
    get_api_key_from_container,
    get_container_type,
    paginate,
    reload_file_parent,
)

log = logging.getLogger(__name__)


SDK_MODELS = {
    "project": "Project",
    "subject": "Subject",
    "session": "Session",
    "acquisition": "Acquisition",
    "file": "FileEntry",
    "analysis": "AnalysisOutput",
}


class Walker(Process):  # pylint: disable=too-many-instance-attributes
    """Process to walk the Flywheel hierarchy.

    NOTE: Every container in the walker should have a `container_type`
    attribute.  All of the containers that the `walker` adds, i.e. via
    `queue_children` have their container_type known and set via the `add_ctype`
    function.  And all containers added via `add` have their container type
    determined.

    If containers are manually added to the deque without container_type
    attributes, walker will raise AttributeErrors
    """

    def __init__(
        self,
        api_key: str,
        root_id: str,
        config: Optional[WalkerConfig] = None,
    ):
        """Initialize a hierarchy walker.

        Args:
            api_key (str): API key to connect to Flywheel site.
            root_id (str): ID of root container.
            config (Optional[CurationConfig]): Config for the walker.
        """
        super().__init__(name="walker")
        self.config = config or WalkerConfig()
        self.api_key = api_key
        self._client: t.Optional[FWClient] = None
        # Configure walking options
        self._exclude = []
        if self.config.stop_level:
            try:
                idx = HIERARCHY.index(self.config.stop_level)
                self._exclude = HIERARCHY[idx:]
            except ValueError:
                log.warning(
                    (
                        f"Expected stop_level to be one of '{HIERARCHY}', found "
                        f"'{self.config.stop_level}'. "
                        "Not excluding any containers"
                    )
                )
        # Get root container
        # NOTE: Containers endpoint returns container_type as an attribute
        root = self.client.get(f"/api/containers/{root_id}", params={"stats": True})
        # Warn if root container is a project and there are a lot of
        # subjects under it: degraded performance for a single-thread.
        sub_count = root.get("stats", {}).get("number_of", {}).get("subjects", 0)
        if sub_count > self.config.subject_warn_limit:
            log.warning(
                f"Project '{root.label}' has {sub_count} subjects. "  # type: ignore
                "Consider using `distribute` and multiprocessing."
            )

        self.deque = deque([root])
        self.queue: Optional[Queue] = None
        self.done: Optional[Event] = None

        # Add deserialization if requested
        self._deserialize = self.config.deserialize

    @property
    def client(self):
        """Get FWClient object."""
        if self._client is not None:
            return self._client
        client = FWClient(
            api_key=self.api_key, client_name=PKG_NAME, client_version=__version__
        )
        # Add exclude-files and slim-container features for
        # exclude_files and exclude_analyses options, respectively.
        x_accept = [
            x for x in (client.headers.get("X-Accept-Feature", "").split(",")) if x
        ]
        features = set(x_accept)
        features.add("pagination")
        features.add("safe-redirect")
        if self.config.exclude_analyses:
            features.add("slim-containers")
        if self.config.exclude_files:
            features.add("exclude-files")
        client.headers["X-Accept-Feature"] = ",".join(features)
        self._client = client
        return self._client

    def run(self):  # pylint: disable=protected-access
        """Run walker process."""
        if len(self.deque) > 1:
            log.error(f"Expected one item in deque, found {self.deque}")
            raise RuntimeError("Multiple root containers found")
        assert self.queue is not None
        assert self.done is not None
        self.done.clear()
        root = self.deque.pop()
        gen = self.get_children(root)
        assert gen
        for item in gen:
            self.queue.put(item)
        # Then iterate over files and analyses
        self.done.set()

    def distribute(self, manager: SyncManager) -> Tuple[Queue, Event]:
        """Distribute top level children to a queue.

        Args:
            manager (SyncManager): multiprocessing Manager.

        Returns:
            Tuple[Queue, Event]:
                - Work queue
                - Event signaling no more containers are to be added
                    to the work queue.
        """
        self.queue = manager.Queue()
        self.done = manager.Event()
        self.start()
        return self.queue, self.done  # type: ignore

    @classmethod
    def from_container(
        cls,
        container: Any,
        api_key: Optional[str] = None,
        config: Optional[WalkerConfig] = None,
    ) -> "Walker":
        """Initialize a walker from a given container.

        Args:
            container (Any): Flywheel SDK model or dictionary of a container.
            api_key (str): API key to connect to Flywheel site.
            config (Optional[WalkerConfig]): Config for the walker.
        """
        if not api_key:
            api_key = get_api_key_from_container(container)
            if not api_key:
                raise RuntimeError(
                    "Cannot determine determine API key, please provide "
                    "the `api_key` keyword argument"
                )
        return Walker(
            api_key,
            container._id,  # pylint: disable=protected-access
            config or WalkerConfig(),
        )

    def deserialize(self, container: Any) -> Any:
        """Deserialize container into Flywheel SDK object."""
        if not self._deserialize:
            return container
        self.sdk_client = None
        try:
            client = getattr(importlib.import_module("flywheel"), "Client")
            # FWClient accepts beginning https:// but flywheel-sdk does not
            api_key = self.api_key.split("/")[-1]
            self.sdk_client = client(api_key)
        except (ModuleNotFoundError, ImportError):
            log.error("Could not find SDK, is it installed?")
            log.warning("Will not attempt to deserialize containers")
            self._deserialize = False
            return container

        models = importlib.import_module("flywheel.models")
        c_type = get_container_type(container)
        model = getattr(models, SDK_MODELS[c_type])
        # If model is none, we'll just let it raise
        # pylint: disable=protected-access
        res = self.sdk_client.api_client._ApiClient__deserialize(container, model)
        # pylint: enable=protected-access
        if getattr(res, "container_type", "") == "file":
            res = reload_file_parent(self.sdk_client, res)
        return res

    def next(self, callback: Optional[Callable[[Any], bool]] = None) -> Any:
        """Return the next element and potentially queues its children.

        Args:
            callback (Optional[Callable[[Any],bool]]).  Optional callback that takes
                in the `next_element` and returns a boolean of whether or not to queue
                its children.  Defaults to None.

        Returns:
            Container: next element in the hierarchy.
        """
        if self.config.depth_first:
            next_element = self.deque.pop()
        else:
            next_element = self.deque.popleft()

        if self.config.reload:
            # Reload the container pulling info, file info, and analyses info
            c_type = get_container_type(next_element)
            # pylint: disable=protected-access
            c_id = next_element._id if c_type != "file" else next_element.file_id
            # pylint: enable=protected-access
            next_element = self.client.get(f"/api/{pluralize(c_type)}/{c_id}")

        if callable(callback) and callback(next_element) is False:
            # User can hook into callback and decide to stop walking.
            # Return next element without queueing children
            return self.deserialize(next_element)

        self.deque.extend(self.get_children(next_element))

        cont = self.deserialize(next_element)
        return cont

    def get_children(self, element: Any) -> Iterator[t.Any]:  # pylint: disable=protected-access
        """Add children of element to the deque."""
        c_type = get_container_type(element)
        # No children of files, analyses or the configured stop-level
        exclusions = self._exclude + ["file", "analysis"]
        if c_type in exclusions:
            return iter([])
        level = HIERARCHY.index(c_type)
        self.deque.extend(add_ctype(element.get("files", []) or [], "file"))

        # Make sure that the analyses attribute is a list before iterating
        analyses = list(add_ctype(element.get("analyses", []) or [], "analysis"))
        if isinstance(analyses, list):
            self.deque.extend(analyses)

        if c_type == "acquisition":
            # No acquisition children containers (just files and analyses)
            return iter([])

        c_level = HIERARCHY[level + 1]
        # NOTE: /api/<container>?filter=parents.<parent_type>=<id> is faster than
        # /api/<parent_type>/<id>/<container>
        # pylint: disable=protected-access
        url = f"/api/{pluralize(c_level)}"
        parent_filter = f"parents.{c_type}={element._id}"
        # pylint: enable=protected-access
        # NOTE: Don't need to 'reload' these here, since analyses and files
        # are returned by default on "filter" endpoints.
        return add_ctype(paginate(self.client, url, parent_filter), c_level)

    def add(self, element: Any):
        """Add element(s) to the walker.

        Args:
            element (Any): Element or list of elements to add to deque
        """
        if isinstance(element, Sequence):
            for el in element:
                c_type = get_container_type(el)
                setattr(el, "container_type", c_type)
            self.deque.extend(element)
        else:
            c_type = get_container_type(element)
            setattr(element, "container_type", c_type)
            self.deque.append(element)

    def is_empty(self):
        """Return True if the walker is empty."""
        return len(self.deque) == 0

    def walk(self, callback: Optional[Callable[[Any], bool]] = None) -> Iterator[Any]:
        """Walk the hierarchy from a root container.

        Args:
            callback (Callable[[Container],bool]).  Optional callback that takes
                in the `next_element` and returns a boolean of whether or not to queue
                its children.  Defaults to None.

        Yields:
            Iterator[Any]: Next element in walker.
        """
        while not self.is_empty():
            yield self.next(callback=callback)
