"""Reporter classes."""

import csv
import json
import logging
from multiprocessing import Process
from multiprocessing.managers import SyncManager
from pathlib import Path
from queue import Queue
from threading import Event
from typing import Any, Dict, Optional

from pydantic import BaseModel

from .config import ReporterConfig

log = logging.getLogger(__name__)


# TODO: Make Curator reorter into a reporter for an analysis gear that can upload a log
#  to each container it curates


class AggregatedReporter(Process):  # pylint: disable=too-many-instance-attributes
    """Creates an aggregated reporter and outputs it in CSV or JSON format.

    This reporter can be used in any gear to create a file report for the actions the
    gear has taken or any errors that need to be reported.
    """

    def __init__(self, config: ReporterConfig) -> None:
        """Initialize aggregated reporter.

        Args:
            config (ReporterConfig): Config

        Raises:
            ValueError: If log format is invalid
            ValueError: If an unsupported/unknown output type is selected.
        """
        super().__init__(name="reporter")
        self.output_path = Path(config.path)
        self.first_record = True
        self.output_type = self.output_path.suffix[1:]
        self.format = config.format
        self.queue: Optional[Queue] = None
        self.done: Optional[Event] = None
        self.keys = list(getattr(self.format, "__annotations__", {}).keys())

        if not self.keys:
            raise ValueError(
                f"No fields found in log format class {self.format.__name__}"
            )

        if self.output_type not in ["csv", "json"]:
            raise ValueError(
                "Only output types of CSV and JSON are currently supported"
            )

        if self.output_path.exists():
            log.warning("Log path already exists, overwriting.")

        if self.output_type == "csv":

            def _writer(fp, to_write: Any) -> None:
                """CSV file writer."""
                writer = csv.writer(fp)
                writer.writerow(to_write)

            # Create the output csv file
            log.info(f"CSV file selected, writing header to '{self.output_path}'")
            self.writer = _writer
            self.write(list(self.keys))
        else:

            def _writer(fp, to_write: Any) -> None:
                """Simple text writer."""
                fp.write(str(to_write))

            # NOTE: For JSON, write a list of JSON objects to the file.
            # Appending won't work because the objects need to be wrapped in a
            # list.  Start the file with an opening list and close the file with
            # a closing bracket to make the resulting file valid json on
            # destructor.

            log.info(f"Touching JSON output '{self.output_path}'")
            self.writer = _writer
            self.write("[\n")

    def __del__(self):
        """Cleanup on object deletion."""
        if self.output_type == "json":
            self.write("]")

    def append_log(
        self,
        record: Optional[BaseModel] = None,
        **kwargs: Optional[Dict[str, Any]],
    ) -> None:
        """Add a message to the report.

        Either an instance of self.format can be
        passed, or keyword arguments.

        Args:
            record (BaseLogRecord, optional): Instance of self.format. Defaults to None
            kwargs (Dict[str,Any], optional): Dictionary or keyword arguments that will
                be inserted. Declared types will be enforced. Defaults to None
        """
        if record:
            rec = record
            if kwargs:
                log.warning(f"Extra kwargs ignored: {kwargs}")
        else:
            rec = self.format(**kwargs)

        self.write_log(rec)

    def write_log(self, rec: BaseModel) -> None:
        """Write a message to the report.

        Args:
            rec (self.format): record
        """
        if self.output_type == "csv":
            self.write(list(rec.model_dump().values()))
        else:
            to_write = ""
            if self.first_record:
                self.first_record = False
            else:
                to_write += ",\n"
            to_write += json.dumps(rec.model_dump(), indent=4)
            self.write(to_write)

    def _write_to_file(self, to_write):
        """Perform actual writing to file."""
        with open(
            self.output_path,
            mode="a",
            encoding="utf-8",
            newline=("" if self.output_type == "csv" else None),
        ) as fp:
            self.writer(fp, to_write)

    def write(self, to_write: Any):
        """Public method to write to a file supporting multithreading."""
        if self.queue and self.done:
            if self.done.is_set():
                log.warning(
                    "Attempted log writing after done has been set: nothing "
                    "more will be written."
                )
                return
            self.queue.put(to_write)
        else:
            self._write_to_file(to_write)

    def multi(self, manager: SyncManager) -> Event:
        """Start separate process for writing to file."""
        self.queue = manager.Queue()
        self.done = manager.Event()
        self.start()
        return self.done

    def run(self):  # pragma: no cover
        """Write worker process."""
        # Coverage tested in tests/test_reporter.py:test_reporter_multi
        assert self.queue is not None
        assert self.done is not None
        while True:
            if self.queue.empty() and self.done.is_set():
                break

            to_write = self.queue.get()
            self._write_to_file(to_write)
