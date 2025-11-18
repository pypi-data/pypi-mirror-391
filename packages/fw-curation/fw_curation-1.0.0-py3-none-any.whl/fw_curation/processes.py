"""Manage curation processes."""

import logging
import time
from multiprocessing import Process
from multiprocessing.managers import Namespace
from queue import Queue
from typing import TYPE_CHECKING, Any, List, Optional, Type

from fw_curation.reporters import AggregatedReporter

from .config import CurationConfig
from .walker import Walker

if TYPE_CHECKING:  # pragma: no cover
    from .curator import HierarchyCurator


log = logging.getLogger(__name__)


def monitor_processes(
    distributor: Process, workers: List[Process], events: Namespace
) -> int:
    """Monitor running curation processes.

    Args:
        distributor (Process): Walker distribute process.
        workers (List[Process]): Worker processes.
        events (Namespace): Events namespace

    Returns:
        int: Return code.
    """
    r_code = 0
    finished = False
    processes = [distributor, *workers]

    # Instead of calling `.join()` on each process, manually block main thread
    #   by checking status of child processes. If the `fail` event has been set
    #   one of the workers encountered an unrecoverable error, kill the other
    #   workers and exit.
    while not finished:
        if events.fail.is_set():
            log.error("Worker failed early, killing other workers...")
            r_code = 1
            for p in processes:
                if p.is_alive():
                    p.terminate()
            finished = True
        # For some reason doesn't work with a generator, so make a list.
        #  pylint: disable=use-a-generator
        elif not any([p.is_alive() for p in processes]):  # pylint: disable=use-a-generator
            finished = True
            #  pylint: enable=use-a-generator
        # Check on status every second
        time.sleep(1)

    # We've finished, but still need to call `join()` so the process can get
    #   cleaned up correctly
    for p in processes:
        p.join()
        e_code = p.exitcode
        log.info(f"{p.name} finished with exit code: {e_code}")
    return r_code


def start_workers(  # pylint: disable=too-many-arguments
    root: "HierarchyCurator",
    queue: Queue,
    parent: Any,
    events: Namespace,
) -> List[Process]:
    """Start worker processes.

    Args:
        cls (Type[HierarchyCurator]): Target class to instantiate in the worker.
        queue (Queue): Work queue.
        parent (Any): Parent container.
        api_key (str): API key for child processes.
        config (CurationConfig): Config object for child processes.
        events (Namespace): Events namespace.
        data (Namespace): Shared data between processes to be populated on
            `cls().data`

    Returns:
        List[Process]: List of processes started.
    """
    num = root.config.workers
    log.info(f"Starting {num} worker processes.")
    workers = []
    for i in range(num):
        log.debug("Initializing worker %d", i)
        proc = Process(
            target=worker,
            args=(
                root.__class__,
                queue,
                parent,
                root.api_key,
                root.config,
                events,
                root.data,
                root.reporter,
            ),
            name=f"curator-worker-{i}",
        )
        proc.start()
        log.debug(f"Started worker {proc.name}")
        workers.append(proc)
    log.info(f"Successfully started {len(workers)} workers.")
    return workers


def worker(  # noqa: PLR0913
    cls: Type["HierarchyCurator"],
    queue: Queue,
    parent: Any,
    api_key: str,
    config: CurationConfig,
    events: Namespace,
    data: Namespace,
    reporter: AggregatedReporter,
) -> None:
    """Target worker function.

    Args:
        cls (Type[HierarchyCurator]): Target class to instantiate.
        queue (Queue): Work queue
        parent (Any): Parent container to set on curator.
        api_key (str): API key
        config (CurationConfig): Config
        events (Namespace): Events namespace
        data (Namespace): Shared data between processes to be populated on
            <HierarchyCurator>.data object.
        reporter: Reporter
    """
    done = events.done
    fail = events.fail
    try:
        subwalker: Optional[Walker] = None
        # Depth first:
        #   Loop through queue and curate each top level container down to the
        #   bottom before moving onto the next in the queue
        if config.depth_first:
            while True:
                # If the queue is empty, it might just be waiting for the next
                # batch of containers, so we also need to check that the `done`
                # event has been set.  If it has, then great we're done and the
                # queue is empty -> break. Otherwise, use `get`s blocking
                # functionality to block until the next element is available
                if queue.empty() and done.is_set():
                    break
                cont = queue.get()
                subwalker = Walker.from_container(cont, api_key=api_key, config=config)
                if config.deserialize:
                    parent = subwalker.deserialize(parent)
                curator = cls(config=config, parent=parent)
                setattr(curator, "data", data)
                setattr(curator, "reporter", reporter)
                curator.curate_single_worker(subwalker, finalize=False)
        # Breadth first:
        #   Loop through queue and add each container to the walker deque.
        #   once all containers are added, we can just call walk on the walker
        #   in breadth-first mode.
        else:
            while True:
                if queue.empty() and done.is_set():
                    break
                cont = queue.get()
                if subwalker is None:
                    subwalker = Walker.from_container(
                        cont, api_key=api_key, config=config
                    )
                else:
                    subwalker.add(cont)
            if config.deserialize:
                parent = subwalker.deserialize(parent)  # type: ignore
            curator = cls(config=config, parent=parent)
            setattr(curator, "data", data)
            curator.curate_single_worker(subwalker, finalize=False)  # type: ignore
    except Exception as exc:  # pylint: disable=broad-except
        log.critical(
            f"Could not finish curation, worker errored early: {exc}", exc_info=True
        )
        # Set fail event which will propagate and terminate other workers.
        fail.set()
