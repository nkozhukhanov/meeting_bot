import sys
from loguru import logger
from config import config

def setup_logger():
    """Configure logging for the application."""
    # Remove default logger
    logger.remove()
    
    # Console logging
    logger.add(
        sys.stdout,
        level=config.log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        colorize=True
    )
    
    # File logging
    logger.add(
        "logs/meeting_bot.log",
        level=config.log_level,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        rotation="10 MB",
        retention="7 days",
        compression="zip"
    )
    
    # Logtail integration (if configured)
    if config.logtail_source_token:
        try:
            from logtail import LogtailHandler
            logtail_handler = LogtailHandler(source_token=config.logtail_source_token)
            logger.add(logtail_handler, level="INFO")
        except ImportError:
            logger.warning("Logtail not installed, skipping cloud logging")
    
    return logger

# Initialize logger
app_logger = setup_logger()