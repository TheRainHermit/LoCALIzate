"""
Logger Utility for LoCALIzate Backend
====================================

Logging configuration and utilities for the application.

Features:
    - Structured JSON logging for production
    - Colored console logging for development
    - Request context logging (request ID, user ID)
    - Log rotation for file logging
    - Performance logging helpers

Usage:
    from app.utils.logger import setup_logging, get_logger
    
    # Setup logging (call once at startup)
    setup_logging()
    
    # Get logger instance
    logger = get_logger(__name__)
    
    # Use logger
    logger.info("Application started")
    logger.error("Something went wrong", exc_info=True)
"""

import os
import sys
import json
import logging
import logging.handlers
from typing import Optional, Dict, Any, Union
from datetime import datetime
from contextvars import ContextVar

from app.core.config import settings

# Context variables for request tracking
_request_id_var: ContextVar[Optional[str]] = ContextVar("request_id", default=None)
_user_id_var: ContextVar[Optional[str]] = ContextVar("user_id", default=None)


# =====================================================
# CUSTOM LOGGING FORMATTERS
# =====================================================

class JSONFormatter(logging.Formatter):
    """
    JSON formatter for structured logging.
    Outputs logs as JSON objects for easy parsing by log aggregators.
    """
    
    def __init__(self, include_context: bool = True):
        super().__init__()
        self.include_context = include_context
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record as JSON.
        
        Args:
            record: Log record
        
        Returns:
            JSON string
        """
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        # Add request context
        if self.include_context:
            request_id = _request_id_var.get()
            if request_id:
                log_entry["request_id"] = request_id
            
            user_id = _user_id_var.get()
            if user_id:
                log_entry["user_id"] = user_id
        
        # Add extra fields from record
        if hasattr(record, "extra"):
            for key, value in record.extra.items():
                log_entry[key] = value
        
        return json.dumps(log_entry, ensure_ascii=False)


class ColoredFormatter(logging.Formatter):
    """
    Colored formatter for console output in development.
    """
    
    # ANSI color codes
    COLORS = {
        "DEBUG": "\033[36m",     # Cyan
        "INFO": "\033[32m",      # Green
        "WARNING": "\033[33m",   # Yellow
        "ERROR": "\033[31m",     # Red
        "CRITICAL": "\033[35m",  # Magenta
        "RESET": "\033[0m"       # Reset
    }
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record with colors.
        
        Args:
            record: Log record
        
        Returns:
            Colored string
        """
        # Get color for level
        color = self.COLORS.get(record.levelname, self.COLORS["RESET"])
        
        # Format timestamp
        timestamp = datetime.fromtimestamp(record.created).strftime("%Y-%m-%d %H:%M:%S")
        
        # Get request ID if available
        request_id = _request_id_var.get()
        request_id_str = f"[{request_id}] " if request_id else ""
        
        # Format message
        formatted = (
            f"{color}{timestamp} "
            f"[{record.levelname}] "
            f"{request_id_str}"
            f"{record.name}:{record.lineno} "
            f"{record.getMessage()}"
            f"{self.COLORS['RESET']}"
        )
        
        # Add exception if present
        if record.exc_info:
            formatted += f"\n{self.formatException(record.exc_info)}"
        
        return formatted


# =====================================================
# CUSTOM LOGGER CLASS
# =====================================================

class ContextLogger(logging.Logger):
    """
    Custom logger with context support.
    """
    
    def _log(self, level, msg, args, exc_info=None, extra=None, stack_info=False, **kwargs):
        """Override to add request context to extra."""
        if extra is None:
            extra = {}
        
        # Add request context
        request_id = _request_id_var.get()
        if request_id:
            extra["request_id"] = request_id
        
        user_id = _user_id_var.get()
        if user_id:
            extra["user_id"] = user_id
        
        super()._log(level, msg, args, exc_info, extra, stack_info, **kwargs)
    
    def log_with_context(self, level: int, msg: str, context: Dict[str, Any], **kwargs):
        """
        Log message with additional context.
        
        Args:
            level: Log level
            msg: Log message
            context: Additional context data
            **kwargs: Extra arguments
        """
        extra = kwargs.pop("extra", {})
        extra["extra"] = context
        self.log(level, msg, extra=extra, **kwargs)


# =====================================================
# LOGGING CONFIGURATION
# =====================================================

def setup_logging(
    log_level: Optional[str] = None,
    log_format: Optional[str] = None,
    log_file: Optional[str] = None
):
    """
    Configure logging for the application.
    
    Args:
        log_level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_format: Log format (json or text)
        log_file: Path to log file (optional)
    """
    # Use settings or defaults
    level = log_level or settings.LOG_LEVEL
    format_type = log_format or settings.LOG_FORMAT
    file_path = log_file or settings.LOG_FILE
    
    # Convert level string to int
    log_level_int = getattr(logging, level.upper(), logging.INFO)
    
    # Set custom logger class
    logging.setLoggerClass(ContextLogger)
    
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level_int)
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level_int)
    
    if format_type == "json" and not settings.is_development:
        console_handler.setFormatter(JSONFormatter())
    else:
        console_handler.setFormatter(ColoredFormatter())
    
    root_logger.addHandler(console_handler)
    
    # File handler (if specified)
    if file_path:
        # Create directory if needed
        log_dir = os.path.dirname(file_path)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
        
        # Rotating file handler (10MB per file, keep 5 backups)
        file_handler = logging.handlers.RotatingFileHandler(
            file_path,
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=5,
            encoding="utf-8"
        )
        file_handler.setLevel(log_level_int)
        
        if format_type == "json":
            file_handler.setFormatter(JSONFormatter())
        else:
            file_handler.setFormatter(logging.Formatter(
                "%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            ))
        
        root_logger.addHandler(file_handler)
    
    # Set logging levels for third-party libraries
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    
    # Log startup message
    logger = get_logger(__name__)
    logger.info(f"Logging configured: level={level}, format={format_type}")
    if file_path:
        logger.info(f"Log file: {file_path}")


def get_logger(name: str) -> ContextLogger:
    """
    Get logger instance.
    
    Args:
        name: Logger name (usually __name__)
    
    Returns:
        ContextLogger instance
    """
    return logging.getLogger(name)


# =====================================================
# CONTEXT MANAGEMENT
# =====================================================

def set_request_context(request_id: str, user_id: Optional[str] = None):
    """
    Set request context for logging.
    
    Args:
        request_id: Unique request ID
        user_id: User ID (optional)
    """
    _request_id_var.set(request_id)
    if user_id:
        _user_id_var.set(user_id)


def clear_request_context():
    """Clear request context."""
    _request_id_var.set(None)
    _user_id_var.set(None)


def get_request_id() -> Optional[str]:
    """Get current request ID."""
    return _request_id_var.get()


def get_user_id() -> Optional[str]:
    """Get current user ID."""
    return _user_id_var.get()


# =====================================================
# CONTEXT MANAGER
# =====================================================

class LogContext:
    """
    Context manager for temporary log context.
    
    Usage:
        with LogContext(request_id="123", user_id="456"):
            logger.info("This will have context")
    """
    
    def __init__(self, request_id: Optional[str] = None, user_id: Optional[str] = None):
        self.request_id = request_id
        self.user_id = user_id
        self._old_request_id = None
        self._old_user_id = None
    
    def __enter__(self):
        self._old_request_id = _request_id_var.get()
        self._old_user_id = _user_id_var.get()
        
        if self.request_id:
            _request_id_var.set(self.request_id)
        if self.user_id:
            _user_id_var.set(self.user_id)
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        _request_id_var.set(self._old_request_id)
        _user_id_var.set(self._old_user_id)


# =====================================================
# LOGGING HELPERS
# =====================================================

def log_request(logger: ContextLogger, method: str, path: str, status_code: int, duration_ms: float):
    """
    Log HTTP request.
    
    Args:
        logger: Logger instance
        method: HTTP method
        path: Request path
        status_code: Response status code
        duration_ms: Request duration in milliseconds
    """
    log_level = logging.ERROR if status_code >= 500 else logging.WARNING if status_code >= 400 else logging.INFO
    
    logger.log(
        log_level,
        f"{method} {path} -> {status_code} ({duration_ms:.2f}ms)",
        extra={
            "method": method,
            "path": path,
            "status_code": status_code,
            "duration_ms": round(duration_ms, 2)
        }
    )


def log_performance(logger: ContextLogger, operation: str, duration_ms: float, **kwargs):
    """
    Log performance metrics.
    
    Args:
        logger: Logger instance
        operation: Operation name
        duration_ms: Duration in milliseconds
        **kwargs: Additional context
    """
    logger.info(
        f"Performance: {operation} took {duration_ms:.2f}ms",
        extra={
            "event": "performance",
            "operation": operation,
            "duration_ms": round(duration_ms, 2),
            **kwargs
        }
    )


def log_error(logger: ContextLogger, error: Exception, context: Optional[Dict] = None):
    """
    Log error with context.
    
    Args:
        logger: Logger instance
        error: Exception instance
        context: Additional context
    """
    extra = {"error_type": type(error).__name__, "error_message": str(error)}
    if context:
        extra.update(context)
    
    logger.error(f"Error: {str(error)}", extra=extra, exc_info=True)


# =====================================================
# TESTING
# =====================================================

def _test():
    """Test logging functionality."""
    print("Testing logger...")
    
    # Setup logging
    setup_logging(log_level="DEBUG", log_format="text")
    
    logger = get_logger(__name__)
    
    # Basic logging
    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")
    
    # Log with context
    set_request_context("test-request-123", "user-456")
    logger.info("Message with request context")
    
    # Log with extra data
    logger.info(
        "User action",
        extra={"action": "login", "user_id": "user-456", "ip": "192.168.1.1"}
    )
    
    # Using context manager
    with LogContext(request_id="nested-request"):
        logger.info("Message in nested context")
    
    # Clear context
    clear_request_context()
    logger.info("Message without context")
    
    # Performance logging
    log_performance(logger, "database_query", 45.3, query="SELECT * FROM users")
    
    # Error logging
    try:
        raise ValueError("Something went wrong")
    except ValueError as e:
        log_error(logger, e, {"user_action": "submit_form"})
    
    print("✅ Logger test completed")


if __name__ == "__main__":
    _test()