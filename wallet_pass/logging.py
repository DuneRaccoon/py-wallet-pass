"""
Logging configuration for py-wallet-pass using loguru.

This module configures loguru for colorful, structured, and insightful logs
across the entire package. It provides a consistent interface for all logging
and diagnostic information.
"""

import sys
import os
from pathlib import Path
from typing import Dict, Any, Optional

from loguru import logger, Logger

# Add a custom SUCCESS level to loguru
success_level = 25  # Between INFO (20) and WARNING (30)
logger.level("SUCCESS", no=success_level, color="<green>")

# Remove default logger
logger.remove()

# Define log format with colors, timestamps, module info, and diagnostic context
LOG_FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
    "<level>{message}</level> "
    "{extra}"
)

# Define different formats for different sinks (console vs file)
CONSOLE_FORMAT = LOG_FORMAT
FILE_FORMAT = LOG_FORMAT

# Add console handler with colors
logger.add(
    sys.stderr,
    format=CONSOLE_FORMAT,
    level="INFO",
    colorize=True,
    backtrace=True,
    diagnose=True,
)

# Set up file logging if log directory is available
LOG_DIR = os.environ.get("WALLET_PASS_LOG_DIR", None)
if LOG_DIR:
    log_path = Path(LOG_DIR)
    if not log_path.exists():
        log_path.mkdir(parents=True, exist_ok=True)
    
    # Add rotating file handler for debugging
    logger.add(
        log_path / "py_wallet_pass.log",
        format=FILE_FORMAT,
        level="DEBUG",
        rotation="10 MB",
        retention="1 week",
        backtrace=True,
        diagnose=True,
    )

# Configure logger to intercept standard library logging
logger.configure(handlers=[{"sink": sys.stderr, "format": CONSOLE_FORMAT}])


def get_logger(name: str) -> Logger:
    """
    Get a logger for the specified module with contextualized information.
    
    Args:
        name: Module name, typically __name__
        
    Returns:
        Configured loguru logger instance with module context
    """
    return logger.bind(module=name)


def with_context(**kwargs) -> Dict[str, Any]:
    """
    Create a context dictionary for adding to logs.
    
    This helper function creates a dictionary that can be used with loguru's
    contextualization feature to add structured contextual information to logs.
    
    Example:
        ```python
        from py_wallet_pass.logging import logger, with_context
        
        pass_id = "pass123"
        template_id = "template456"
        context = with_context(pass_id=pass_id, template_id=template_id)
        
        logger.bind(**context).info("Processing pass")
        ```
    
    Args:
        **kwargs: Key-value pairs to add as context
        
    Returns:
        Dictionary of context variables formatted for loguru
    """
    return kwargs


# Configure exception handling to use loguru
def handle_exception(exc_type, exc_value, exc_traceback):
    """
    Global exception handler to log unhandled exceptions.
    """
    # Skip for KeyboardInterrupt
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    
    # Log the exception
    logger.opt(exception=(exc_type, exc_value, exc_traceback)).error(
        "Unhandled exception:"
    )


# Set the global exception handler
sys.excepthook = handle_exception
