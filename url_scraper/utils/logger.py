# utils/logger.py : A robust logger is essential for monitoring and debugging a production scraper.

import sys
from loguru import logger


def setup_logger():
    """Configures the logger for console and file output."""
    
    logger.remove()  # Remove default handler. 
                     #Loguru automatically adds a default logger that prints to the console.
                     #This line removes the default logger so you can define your own custom ones.
    
    # Console logger
    logger.add(
        sys.stderr,
        level="INFO",
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        colorize=True
    )
    
    # File logger (optional, but good for production)
    # logger.add(
    #     "logs/scraper_{time}.log",
    #     level="DEBUG",
    #     rotation="10 MB",
    #     retention="10 days",
    #     format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
    # )
    
    return logger

app_logger = setup_logger()