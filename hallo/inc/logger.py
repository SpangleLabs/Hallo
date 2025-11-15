import datetime
import logging
import os
import sys
from logging import FileHandler
from typing import Dict, Optional

from hallo.destination import Destination
from hallo.server import Server


class ChatLogFileHandler(FileHandler):
    def __init__(self, dir_path: str):
        self.dir_path = dir_path
        super().__init__(self._calculate_path())

    def _calculate_path(self) -> str:
        now = datetime.datetime.now()
        return os.path.abspath(f"{self.dir_path}/{now.year:04}-{now.month:02}-{now.day:02}.txt")

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
            handler = ChatLogFileHandler(path)
            handler.setFormatter(self.formatter)
            self._handlers[server_name][dest_name] = handler
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

    # Set up chat logging
    chat_logger = logging.getLogger("chat")
    chat_logger.propagate = False
    chat_logger.setLevel(logging.DEBUG)
    chat_console_formatter = logging.Formatter("[{asctime}] [{server.name}] {message}", style="{", datefmt="%H:%M:%S")
    chat_console_handler = logging.StreamHandler(sys.stdout)
    chat_console_handler.setFormatter(chat_console_formatter)
    chat_logger.addHandler(chat_console_handler)
    chat_formatter = logging.Formatter("[{asctime}] {message}", style="{", datefmt="%H:%M:%S")
    chat_log_handler = ChatLogHandler(log_dir)
    chat_log_handler.setFormatter(chat_formatter)
    chat_logger.addHandler(chat_log_handler)

    # Set up root logger
    core_logger = logging.getLogger("")
    formatter = logging.Formatter("{asctime}:{levelname}:{name}:{message}", style="{")
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    core_logger.addHandler(console_handler)

    # Set up hallo logger, for errors and such, to file
    hallo_logger = logging.getLogger("hallo")
    hallo_logger.setLevel(logging.DEBUG)
    log_handler = FileHandler(f"{log_dir}/hallo.log")
    log_handler.setFormatter(formatter)
    hallo_logger.addHandler(log_handler)
