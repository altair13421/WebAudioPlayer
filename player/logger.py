import logging

import json
import os
import time
from logging import Handler
from typing import Dict

import requests


def get_log_level_from_str(log_level_str: str = "debug") -> int:
    log_level_dict = {
        "CRITICAL": logging.CRITICAL,
        "ERROR": logging.ERROR,
        "WARNING": logging.WARNING,
        "NOTICE": logging.getLevelName("NOTICE"),
        "INFO": logging.INFO,
        "DEBUG": logging.DEBUG,
        "NOTSET": logging.NOTSET,
    }

    return log_level_dict.get(log_level_str.upper(), logging.getLevelName("NOTICE"))


class PlainFormatter(logging.Formatter):
    """Adds log levels."""

    def format(self, record: logging.LogRecord) -> str:
        levelname = record.levelname
        level_display = f"{levelname}:"
        formatted_message = super().format(record)
        return f"{level_display.ljust(9)} {formatted_message}"


class ColoredFormatter(logging.Formatter):
    """Custom formatter to add colors to log levels."""

    COLORS = {
        "CRITICAL": "\033[91m",  # Red
        "ERROR": "\033[91m",  # Red
        "WARNING": "\033[93m",  # Yellow
        "NOTICE": "\033[94m",  # Blue
        "INFO": "\033[92m",  # Green
        "DEBUG": "\033[96m",  # Light Green
        "NOTSET": "\033[91m",  # Reset
    }

    def format(self, record: logging.LogRecord) -> str:
        levelname = record.levelname
        if levelname in self.COLORS:
            prefix = self.COLORS[levelname]
            suffix = "\033[0m"
            formatted_message = super().format(record)
            # Ensure the levelname with colon is 9 characters long
            # accounts for the extra characters for coloring
            level_display = f"{prefix}{levelname}{suffix}:"
            return f"{level_display.ljust(18)} {formatted_message}"
        return super().format(record)


def get_standard_formatter() -> ColoredFormatter:
    """Returns a standard colored logging formatter."""
    return ColoredFormatter(
        "%(asctime)s %(filename)30s %(lineno)4s: %(message)s",
        datefmt="%m/%d/%Y %I:%M:%S %p",
    )


def get_plain_formatter() -> PlainFormatter:
    """Returns a plain logging formatter."""
    return PlainFormatter(
        "%(asctime)s %(filename)30s %(lineno)4s: %(message)s",
        datefmt="%m/%d/%Y %I:%M:%S %p",
    )


class LokiHandler(Handler):
    """Custom handler for sending logs to Loki"""

    def __init__(self, url: str, labels: Dict[str, str] = None):
        super().__init__()
        self.url = url
        # print(f"LokiHandler initialized with URL: {self.url}")  # DEBUG
        # print(f"Given LABELS: {labels}")
        self.labels = labels or {
            "job": "music-app",
            "application": "api-service",
            "environment": "development",
        }
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Content-Type": "application/json",
            }
        )


    def format_for_loki(self, record):
        """Format log record for Loki"""
        log_data = {
            "level": record.levelname,
            "message": record.getMessage(),
            "file": record.filename,
            "line": record.lineno,
            "function": record.funcName,
            "logger": record.name,
            "timestamp": f"{time.strftime('%Y-%m-%dT%H:%M:%S', time.gmtime(record.created))}.{int((record.created % 1) * 1000000):06d}Z",
        }

        if hasattr(record, "track_id"):
            log_data["track_id"] = record.track_id
        if hasattr(record, "artists"):
            log_data["artists"] = record.artists
        if hasattr(record, "album"):
            log_data["album"] = record.album
        if hasattr(record, "track_name"):
            log_data["track_name"] = record.track_name

        return json.dumps(log_data)

    def emit(self, record):
        try:
            # print(f"LokiHandler.emit called for: {record.levelname} - {record.getMessage()}")

            log_entry = self.format_for_loki(record)
            timestamp_ns = int(record.created * 1e9)
            # Prepare Loki payload
            payload = {
                "streams": [
                    {"stream": self.labels, "values": [[str(timestamp_ns), log_entry]]}
                ]
            }

            # print(f"Sending to Loki: {self.url}")
            # print(f"Payload: {json.dumps(payload, indent=2)}")

            response = self.session.post(self.url, json=payload, timeout=5)
            # print(f"Loki response: {response.status_code} - {response.text}")

            if response.status_code != 204:
                print(f"Loki request failed: {response.status_code} - {response.text}")

        except requests.exceptions.RequestException as e:
            print(f"Loki network error: {e}")
        except Exception as e:
            print(f"Loki handler error: {e}")
            import traceback

            traceback.print_exc()


def is_loki_available(url: str = "http://172.17.0.1:3100/loki/api/v1/push") -> bool:
    """Check if Loki is reachable"""
    try:
        response = requests.get(url.replace('/loki/api/v1/push', '/ready'), timeout=2)
        return response.status_code == 200
    except:
        return False

def setup_loki_handler(url: str, loki_job: Dict[str, str] = None):
    """Setup direct Loki HTTP handler"""
    loki_endpoint = os.getenv(
        "LOKI_ENDPOINT",
        # "http://loki-gateway.observability.svc.cluster.local/loki/api/v1/push",
        url,
    )
    # print(f"Setting up Loki handler with endpoint: {loki_endpoint}")
    default_job = loki_job or {
        "job": "music-app",
        "environment": os.getenv("ENVIRONMENT", "development"),
        "application": "api-service",
    }

    # print(f"chat logs with job, {default_job}. Loki: {loki_job}")
    loki_handler = LokiHandler(loki_endpoint, default_job)

    loki_handler.setFormatter(logging.Formatter("%(message)s"))
    return loki_handler


def setup_logger(name: str, level: int = get_log_level_from_str()) -> logging.Logger:
    logger = logging.getLogger(name)
    log_level = get_log_level_from_str()
    if logger.handlers:
        return logger

    logger.setLevel(log_level)
    formatter = get_standard_formatter()
    handler = logging.StreamHandler()
    handler.setLevel(log_level)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    url = "http://172.17.0.1:3100/loki/api/v1/push" # For Docker Cause, Yeah
    # url = "http://127.0.0.1:3100/loki/api/v1/push" # Localhost Testing
    # Loki Handler
    if is_loki_available(url):
        loki_handler = setup_loki_handler(url)
        if loki_handler:
            loki_handler.setLevel(log_level)
            logger.addHandler(loki_handler)
            print("Loki handler added successfully")
    else:
        print("Loki not available, skipping Loki handler")
    if not logger.hasHandlers():
        logger.addHandler(handler)
    # Return Normal
    return logger

logger = setup_logger(__name__)
logger.info("Test message to check if Loki handler works")
