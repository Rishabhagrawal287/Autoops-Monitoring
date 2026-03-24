import os
import sys
from datetime import datetime


class Logger:
    _instance = None  # Singleton instance

    LEVELS = {
        "DEBUG": 10,
        "INFO": 20,
        "ERROR": 30
    }

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
        return cls._instance

    def __init__(self, log_dir="logs", log_file="autoops.log",
                 level="INFO", max_size_mb=5, console=True):

        if hasattr(self, "_initialized"):
            return

        self.log_dir = log_dir
        self.log_file = log_file
        self.full_path = os.path.join(self.log_dir, self.log_file)
        self.level = self.LEVELS.get(level.upper(), 20)
        self.max_size = max_size_mb * 1024 * 1024
        self.console = console

        self._ensure_log_directory()
        self._initialized = True

    def _ensure_log_directory(self):
        try:
            if not os.path.exists(self.log_dir):
                os.makedirs(self.log_dir)
        except Exception as e:
            print(f"CRITICAL: Failed to create log directory: {e}")
            sys.exit(1)

    def _rotate_if_needed(self):
        if os.path.exists(self.full_path):
            if os.path.getsize(self.full_path) > self.max_size:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                new_name = f"autoops_{timestamp}.log"
                os.rename(self.full_path,
                          os.path.join(self.log_dir, new_name))

    def _write(self, level_name, message):
        if self.LEVELS[level_name] < self.level:
            return

        try:
            self._rotate_if_needed()

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            formatted = f"[{timestamp}] [{level_name}] {message}\n"

            with open(self.full_path, "a", encoding="utf-8") as file:
                file.write(formatted)

            if self.console:
                print(formatted.strip())

        except Exception as e:
            print(f"CRITICAL: Failed to write log: {e}")
            sys.exit(1)

    def debug(self, message):
        self._write("DEBUG", message)

    def info(self, message):
        self._write("INFO", message)

    def error(self, message):
        self._write("ERROR", message)