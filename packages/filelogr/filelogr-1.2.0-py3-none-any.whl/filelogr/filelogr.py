"""
Logger Module (filelogr.py)

Provides a class `Logger` to handle logging actions to a file,
optionally printing them to the console.

You must call Logger.configure(data_dir, log_file) before use.
- data_dir: folder where log file will be saved
- log_file: filename only (relative, not absolute)
"""

import datetime
import os
import sys

# Default paths (used until configure() is called)
DATA_DIR = os.path.join(os.getcwd(), "Placeholder_Data")
LOG_FILE = os.path.join(DATA_DIR, "Placeholder_Log.txt")


class Logger:
    _data_dir = DATA_DIR
    _log_file = LOG_FILE
    _configured = False

    @classmethod
    def configure(cls, data_dir: str = None, log_file: str = None):
        """
        Set custom paths for logging.
        Both data_dir and log_file must be provided.
        The log_file must be a relative filename (not an absolute path).
        """
        if not data_dir or not log_file:
            print("Logger not configured: both data_dir and log_file must be provided.")
            return

        if os.path.isabs(log_file):
            print("Logger not configured: absolute paths for log_file are not allowed.")
            return

        cls._data_dir = data_dir
        cls._log_file = os.path.join(cls._data_dir, log_file)

        os.makedirs(cls._data_dir, exist_ok=True)
        cls._configured = True

    @classmethod
    def log_action(cls, action: str, print_to_console: bool = True, separator: bool = False, tag: str = None):
        """
        Logs a message to the log file.
        - print_to_console: whether to also print it to the terminal
        - separator: logs a message with no timestamp (like dividers)
        - tag: optional string tag like "INFO", "ERROR", etc.
        """

        # safety: auto-create placeholder dir if unconfigured
        if not cls._configured:
            os.makedirs(os.path.dirname(cls._log_file), exist_ok=True)

        message = f"[{tag}] {action}" if tag else action

        if print_to_console:
            print(message)

        try:
            with open(cls._log_file, 'a', encoding='utf-8') as f:
                if separator:
                    f.write(f"{message}\n")
                else:
                    timestamp = datetime.datetime.now().strftime("%m-%d-%Y %H:%M:%S")
                    f.write(f"[{timestamp}] {message}\n")
        except Exception as e:
            print(f"Logging error: {e}", file=sys.stderr)
