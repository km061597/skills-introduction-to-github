"""
Structured logging configuration for SmartAmazon API

Provides JSON-formatted logs with request context, correlation IDs, and performance metrics
"""
import logging
import sys
import json
from datetime import datetime
from typing import Any, Dict
from contextvars import ContextVar
import uuid


# Context variables for request tracking
request_id_var: ContextVar[str] = ContextVar('request_id', default='')
user_id_var: ContextVar[str] = ContextVar('user_id', default='')


class JSONFormatter(logging.Formatter):
    """
    Custom JSON formatter for structured logging
    """

    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record as JSON

        Args:
            record: Log record

        Returns:
            JSON-formatted log string
        """
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }

        # Add request context if available
        request_id = request_id_var.get()
        if request_id:
            log_data["request_id"] = request_id

        user_id = user_id_var.get()
        if user_id:
            log_data["user_id"] = user_id

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": self.formatException(record.exc_info)
            }

        # Add extra fields
        if hasattr(record, 'extra_data'):
            log_data.update(record.extra_data)

        return json.dumps(log_data)


def setup_logging(level: str = "INFO") -> logging.Logger:
    """
    Configure logging for the application

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    Returns:
        Configured logger instance
    """
    # Create logger
    logger = logging.getLogger("smartamazon")
    logger.setLevel(getattr(logging, level.upper()))

    # Remove existing handlers
    logger.handlers.clear()

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level.upper()))

    # Set JSON formatter
    formatter = JSONFormatter()
    console_handler.setFormatter(formatter)

    # Add handler to logger
    logger.addHandler(console_handler)

    # Prevent propagation to root logger
    logger.propagate = False

    return logger


def get_logger(name: str = "smartamazon") -> logging.Logger:
    """
    Get a logger instance

    Args:
        name: Logger name

    Returns:
        Logger instance
    """
    return logging.getLogger(name)


def log_with_context(logger: logging.Logger, level: str, message: str, **kwargs):
    """
    Log a message with additional context

    Args:
        logger: Logger instance
        level: Log level
        message: Log message
        **kwargs: Additional context fields
    """
    # Get log method
    log_method = getattr(logger, level.lower())

    # Create a custom log record with extra data
    extra_record = type('obj', (object,), {'extra_data': kwargs})()

    log_method(message, extra={'extra_data': kwargs})


def set_request_context(request_id: str = None, user_id: str = None):
    """
    Set request context for logging

    Args:
        request_id: Unique request identifier
        user_id: User identifier
    """
    if request_id:
        request_id_var.set(request_id)
    else:
        request_id_var.set(str(uuid.uuid4()))

    if user_id:
        user_id_var.set(user_id)


def clear_request_context():
    """
    Clear request context
    """
    request_id_var.set('')
    user_id_var.set('')


# Performance logging decorator
def log_performance(logger: logging.Logger):
    """
    Decorator to log function performance

    Args:
        logger: Logger instance

    Returns:
        Decorated function
    """
    def decorator(func):
        import time
        from functools import wraps

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                log_with_context(
                    logger,
                    "info",
                    f"{func.__name__} completed",
                    function=func.__name__,
                    duration_ms=round(duration * 1000, 2),
                    status="success"
                )
                return result
            except Exception as e:
                duration = time.time() - start_time
                log_with_context(
                    logger,
                    "error",
                    f"{func.__name__} failed",
                    function=func.__name__,
                    duration_ms=round(duration * 1000, 2),
                    status="error",
                    error=str(e)
                )
                raise

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                log_with_context(
                    logger,
                    "info",
                    f"{func.__name__} completed",
                    function=func.__name__,
                    duration_ms=round(duration * 1000, 2),
                    status="success"
                )
                return result
            except Exception as e:
                duration = time.time() - start_time
                log_with_context(
                    logger,
                    "error",
                    f"{func.__name__} failed",
                    function=func.__name__,
                    duration_ms=round(duration * 1000, 2),
                    status="error",
                    error=str(e)
                )
                raise

        # Return appropriate wrapper
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


# Initialize default logger
setup_logging()
