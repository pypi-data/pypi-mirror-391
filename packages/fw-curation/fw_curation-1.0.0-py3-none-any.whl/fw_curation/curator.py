"""Curator class module."""

import abc
import contextlib
import importlib
import logging
import time
import typing as t
from multiprocessing import Manager
from multiprocessing.managers import DictProxy, SyncManager
from pickle import PickleError
from threading import Lock

from fw_client import FWClient
from fw_utils import attrify

from .config import CurationConfig
from .processes import monitor_processes, start_workers
from .reporters import AggregatedReporter
from .utils import get_container_type
from .walker import Walker

log = logging.getLogger(__name__)

try:
    import flywheel  # noqa: F401

    HAVE_SDK = True
except (ModuleNotFoundError, ImportError):  # pragma: no cover
    HAVE_SDK = False
    log.debug("SDK not found, falling back to FWClient")

if t.TYPE_CHECKING:
    from flywheel import Client  # noqa: F401


class Curator(abc.ABC):
    """Abstract curator base class."""

    def __init__(
        self,
        config: t.Optional[CurationConfig] = None,
        parent: t.Optional[t.Any] = None,
        **kwargs: t.Optional[t.Dict[str, t.Any]],
    ) -> None:
        """An abstract class to be implemented by the user.

        Args:
            config (CurationConfig, optional): Config object. Defaults to None.
            parent (Any, optional): Parent container. Defaults to None.
        """
        self.config = config or CurationConfig()
        self.data: t.Union[dict, DictProxy] = {}
        # Lock used for `open` method in multiprocess mode.
        self.lock: t.Optional[Lock] = None

        # Allow passing in a parent container to be set on class
        #   This is used when initializing curator workers so that
        #   the workers have the root container as an attribute.
        if parent:
            c_type = parent.container_type
            setattr(self, c_type, parent)

        if self.config.report:
            self.reporter = AggregatedReporter(self.config)

        # Set extra attributes on the class via kwargs
        for k, v in kwargs.items():
            setattr(self, k, v)

    @contextlib.contextmanager
    def open(self, path, mode="r", encoding="utf-8"):  # noqa: D402
        """Wrapper around <builtins>.open() that is thread safe.

        Args:
            path (str): Path of file to open.
            mode (str): mode to be passed into `open`. Default 'r'.
            encoding (str): Encoding schema to use.
        """
        if self.lock:
            # Let this raise an AttributeError if lock is still None
            self.lock.acquire()
        try:
            with open(path, mode=mode, encoding=encoding) as fp:
                yield fp
        finally:
            if self.lock:
                self.lock.release()

    @abc.abstractmethod
    def curate_container(self, container: t.Any):  # pragma: no cover
        """Curate a generic container.

        Args:
            container (Any): A Flywheel container or its dictionary representation.
        """
        raise NotImplementedError()

    def finalize(self):
        """Use for doing stuff after curation."""


class HierarchyCurator(Curator):
    """An abstract class to curate the Flywheel Hierarchy.

    The user-defined Curator class should inherit from
    HierarchyCurator.

    This class defines abstract methods for each container type (e.g
    `curate_project`) (i.e. methods that need to be defined in the child
    curator Class implemented by the user, see example scripts in the example
    folder). Such methods are decorated with the `abc.abstractmethod` decorator
    in this abstract class.

    Validation methods are also defined for each container type. Validation
    methods become handy when, for example, curating a file is a time
    consuming process; it allows for marking a file during the curation
    method and checking for that mark elsewhere in the validate method.

    """

    def _get_client(  # pylint: disable=attribute-defined-outside-init
        self, walker: Walker
    ):
        """Set api-key and client from Walker."""
        self.api_key = walker.client.api_key  # type: ignore
        if HAVE_SDK:
            client_cls = getattr(importlib.import_module("flywheel"), "Client")
            assert client_cls is not None
            # FWClient accepts beginning https:// but flywheel-sdk does not
            api_key = self.api_key.split("/")[-1]
            self.client = client_cls(api_key)
        else:
            self.client = FWClient(api_key=self.api_key)

    def _curate_root(self, walker: Walker) -> t.Any:
        """Curate root container.  Helper for curate_multi."""
        log.info("Curating root container.")
        parent_cont = walker.deque[0]
        if self.validate_container(parent_cont):
            self.curate_container(parent_cont)
        if hasattr(parent_cont, "to_dict"):
            # SDK type, convert to AttrDict for pickling
            parent_cont = attrify(parent_cont.to_dict())  # type: ignore
        return parent_cont

    def _data_to_proxy(self, manager: SyncManager):
        """Convert data dictionary to managed proxy dictionary."""
        data = t.cast(t.Dict[str, t.Any], manager.dict())
        try:
            for k, v in self.data.items():
                data[k] = v
        except PickleError as exc:
            log.error(
                "Could not start multiprocessing mode, class data contained "
                "non-picklable object In order to use multiprocessing mode, "
                "all data stored under <self>.data must be pickleable"
            )
            raise RuntimeError("Invalid instance data") from exc
        self.data = data

    def curate_single_worker(self, walker: Walker, finalize=True):
        """Run single worker curation.

        Args:
            walker (Walker): Hierarchy Walker.
            finalize (bool, optional): Whether to run finalize. Defaults to True.
        """
        self._get_client(walker)
        for cont in walker.walk():
            if self.validate_container(cont):
                self.curate_container(cont)
        if finalize:
            self.finalize()

    def curate_multi_worker(self, walker: Walker) -> int:
        """Run multiple worker curation.

        Args:
            walker (Walker): Hierarchy Walker

        Returns:
            int: return code.
        """
        t1 = int(time.time() * 1000)
        self._get_client(walker)
        # Create a Manager process to manage access to shared data
        with Manager() as mgr:
            # Set lock for using `open` method.
            self.lock = mgr.Lock()  # pylint: disable=no-member
            # Convert self.data to managed proxy
            self._data_to_proxy(mgr)
            # Curate first container.
            parent = self._curate_root(walker)
            # Start walker process
            log.info("Starting hierarchy walker process.")
            work_queue, done = walker.distribute(mgr)

            # Set up events namespace
            events = mgr.Namespace()
            events.done = done
            events.fail = mgr.Event()

            # Init reporter if requested
            if self.reporter is not None:
                log.info("Starting reporter process")
                done_reporting = self.reporter.multi(mgr)
                events.done_reporting = done_reporting

            t2 = int(time.time() * 1000)
            log.debug("Setup finished, took: %s ms", t2 - t1)
            # Start workers
            workers = start_workers(
                self,
                work_queue,
                parent,
                events,
            )
            t3 = int(time.time() * 1000)
            log.debug("Workers started, took: %s ms", t3 - t2)

            # Start monitoring processes
            r_code = monitor_processes(walker, workers, events)

            # If a reporter was instantiated, send it the termination signal.
            if self.reporter is not None:
                events.done_reporting.set()  # type: ignore
                self.reporter.join()
            # Finally call self.finalize() if defined.
            self.finalize()
        return r_code

    def curate(self, walker: Walker) -> int:
        """Run curation.

        If `workers` config is 0, run in single worker mode, otherwise, run in
        multi-worker mode with the specified number of workers

        Args:
            walker (Walker): Hierarchy Walker.

        Returns:
            int: return code.
        """
        if self.config.workers > 0:
            return self.curate_multi_worker(walker)
        try:
            self.curate_single_worker(walker)
            return 0
        except Exception as exc:  # pylint: disable=broad-except
            log.error(f"Curation exception: {exc}", exc_info=True)
            return 1

    def validate_container(self, container: t.Any) -> bool:
        """Decide whether or not a container should be curated.

        Args:
            container (Container): Container to make decision on.

        Returns:
            bool: Whether or not it should be curated
        """
        c_type = get_container_type(container)
        validate_method = getattr(self, f"validate_{c_type}")
        return validate_method(container)  # type: ignore

    def curate_container(self, container: t.Any):
        """Curate a generic container.

        Args:
            container (Container): A Flywheel container.
        """
        c_type = get_container_type(container)
        curate_method = getattr(self, f"curate_{c_type}")
        setattr(self, c_type, container)
        curate_method(container)

    def curate_project(self, project: t.Any):  # pragma: no cover
        """Curate a project."""

    # pylint: disable=unused-argument
    def curate_subject(self, subject: t.Any):  # pragma: no cover
        """Curate a subject."""

    def curate_session(self, session: t.Any):  # pragma: no cover
        """Curate a session."""

    def curate_acquisition(self, acquisition: t.Any):  # pragma: no cover
        """Curate an acquisition."""

    def curate_analysis(self, analysis: t.Any):  # pragma: no cover
        """Curate an analysis."""

    def curate_file(self, file_: t.Any):  # pragma: no cover
        """Curate a file."""

    def validate_project(self, project: t.Any):  # pragma: no cover
        """Returns True if project needs curation, False otherwise."""
        return True

    def validate_subject(self, subject: t.Any):  # pragma: no cover
        """Returns True if subject needs curation, False otherwise."""
        return True

    def validate_session(self, session: t.Any):  # pragma: no cover
        """Returns True if session needs curation, False otherwise."""
        return True

    def validate_acquisition(self, acquisition: t.Any):  # pragma: no cover
        """Returns True if acquisition needs curation, False otherwise."""
        return True

    def validate_analysis(self, analysis: t.Any):  # pragma: no cover
        """Returns True if analysis needs curation, False otherwise."""
        return True

    def validate_file(self, file_: t.Any):  # pragma: no cover
        """Returns True if file_ needs curation, False otherwise."""
        return True

    # pylint: enable=unused-argument


class FileCurator(Curator):
    """Single file curator."""

    def curate_container(self, container: t.Any) -> None:
        """Curate a generic container.

        Args:
            container (Dict or Container): A Flywheel file.
        """
        if self.validate_file(container):
            self.curate_file(container)

    # pylint: disable=unused-argument
    def curate_file(self, file_: t.Any) -> None:  # pragma: no cover
        """Curate a file."""

    def validate_file(self, file_: t.Any) -> bool:  # pragma: no cover
        """Returns True if a file_ needs curation, False otherwise."""
        return True

    # pylint: enable=unused-argument
