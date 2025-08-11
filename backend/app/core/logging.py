import logging
import sys
import os
from pathlib import Path

# Create logs directory
log_dir = Path(__file__).parent.parent.parent / "logs"
log_dir.mkdir(exist_ok=True)

# Get log level from environment
log_level = getattr(logging, os.getenv("LOG_LEVEL", "INFO").upper())

# Configure logging with proper encoding
logging.basicConfig(
    level=log_level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        # Use UTF-8 encoding for console output
        logging.StreamHandler(sys.stdout),
        # Use UTF-8 encoding for file output
        logging.FileHandler(log_dir / "app.log", encoding="utf-8"),
    ],
)

# Set console handler encoding to UTF-8 if possible
for handler in logging.root.handlers:
    if (isinstance(handler, logging.StreamHandler) and
            handler.stream == sys.stdout):
        # Try to set UTF-8 encoding for Windows
        try:
            handler.stream.reconfigure(encoding="utf-8")
        except (AttributeError, OSError):
            # If reconfigure fails (older Python or system limitation),
            # we'll fall back to ASCII-safe logging
            pass

logger = logging.getLogger(__name__)


# Helper function for Windows-safe logging
def safe_log(level, message, *args, **kwargs):
    """Log message with fallback for encoding issues"""
    try:
        getattr(logger, level)(message, *args, **kwargs)
    except UnicodeEncodeError:
        # Replace emoji/unicode with ASCII equivalents
        safe_message = message.encode("ascii", errors="replace").decode(
            "ascii")
        getattr(logger, level)(safe_message, *args, **kwargs)


# Example usage in your code:
# from app.core.logging import logger, safe_log
# logger.debug("Debug message")
# safe_log("info", "Message with emoji 🚀")
