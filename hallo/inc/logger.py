import datetime
import logging
import os
import sys
from logging import FileHandler
from threading import Lock
from typing import Dict, Optional

from hallo.destination import Destination
from hallo.errors import Error
from hallo.events import Event
from hallo.server import Server


class ChatLogFileHandler(FileHandler):
    def __init__(self, dir_path: str):
        self.dir_path = dir_path
        super().__init__(self._calculate_path())

    def _calculate_path(self) -> str:
        now = datetime.datetime.now()
        return os.path.abspath(f"{self.dir_path}/{now.year}-{now.month}-{now.day}.txt")

    def _swap_stream(self, new_path: str) -> None:
        self.acquire()
        try:
            self.close()
            self.baseFilename = new_path
            self.stream = self._open()
        finally:
            self.release()

    def emit(self, record: logging.LogRecord) -> None:
        # Check if date has changed
        new_path = self._calculate_path()
        if self.baseFilename != new_path:
            self._swap_stream(new_path)
        super().emit(record)


class ChatLogHandler(logging.Handler):
    def __init__(self, root_dir: str):
        super().__init__()
        self.root_dir = root_dir
        self._handlers: Dict[str, Dict[str, logging.Handler]] = {}

    # noinspection PyUnresolvedReferences
    def _get_handler(self, record: logging.LogRecord) -> Optional[logging.Handler]:
        if not hasattr(record, "server") or not isinstance(record.server, Server):
            return None
        server_name = record.server.name
        if server_name not in self._handlers:
            self._handlers[server_name] = {}
        if not hasattr(record, "destination") or not isinstance(record.destination, Destination):
            dest_name = "@"
        else:
            if not record.destination.logging:
                return None
            dest_name = record.destination.name
        if dest_name not in self._handlers[server_name]:
            path = f"{self.root_dir}/{server_name}/{dest_name}/"
            os.makedirs(path, exist_ok=True)
            self._handlers[server_name][dest_name] = ChatLogFileHandler(path)
        return self._handlers[server_name][dest_name]

    def emit(self, record: logging.LogRecord) -> None:
        try:
            handler = self._get_handler(record)
            if handler is not None:
                handler.emit(record)
        except Exception:
            self.handleError(record)

    def close(self) -> None:
        self.acquire()
        try:
            for server in self._handlers:
                for destination in self._handlers[server]:
                    self._handlers[server][destination].close()
            super().close()
        finally:
            self.release()


def setup_logging() -> None:
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    formatter = logging.Formatter("{asctime}:{levelname}:{name}:{message}", style="{")
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    # Set up chat logging
    chat_logger = logging.getLogger("chat")
    chat_logger.setLevel(logging.DEBUG)
    chat_logger.addHandler(console_handler)
    chat_formatter = logging.Formatter("[{asctime}] {message}", style="{", datefmt="%H:%M:%S")
    chat_log_handler = ChatLogHandler(log_dir)
    chat_log_handler.setFormatter(chat_formatter)
    chat_logger.addHandler(chat_log_handler)

    # Set up core logger, for errors and such
    hallo_logger = logging.getLogger("hallo")
    hallo_logger.addHandler(console_handler)
    log_handler = FileHandler(f"{log_dir}/hallo.log")
    log_handler.setFormatter(formatter)
    hallo_logger.addHandler(log_handler)

    # Set up usage logger
    usage_logger = logging.getLogger("usage")
    usage_logger.setLevel(logging.DEBUG)
    usage_handler = FileHandler(f"{log_dir}/usage.log")
    usage_handler.setFormatter(formatter)
    usage_logger.addHandler(usage_handler)


def indent_all_but_first_line(text):
    return text.replace("\n", "\n   ")


logger = logging.getLogger(__name__)


class Logger:
    """
    Logging class. This is created and stored by the Hallo object.
    It exists in order to provide a single entry point to all logging.
    """

    def __init__(self, hallo):
        """
        Constructor
        """
        self.hallo = hallo
        self._lock = Lock()

    def log(self, loggable):
        """
        The function which actually writes the logs.
        :type loggable: events.Event | errors.Error
        """
        # Log the event
        if isinstance(loggable, Event):
            loggable.log()
        if isinstance(loggable, Error):
            logger.error(loggable.get_log_line())
