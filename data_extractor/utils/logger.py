# data_extractor/utils/logger.py

import sys
from loguru import logger

def setup_logger():
    """Configures the logger for console and file output."""
    logger.remove()
    
    logger.add(
        sys.stderr,
        level="INFO",
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        colorize=True
    )
    
    return logger

# This is the line that makes the variable available for import
app_logger = setup_logger()

"""
### **Action Required**

1.  Make the one-line change in `data_extractor/utils/geo_validator.py`.
2.  Quickly verify the content of `data_extractor/utils/logger.py` matches the code above.
3.  From your **project root directory (`DOCTOR DATA SCRAPPER`)**, run the command again:
    ```bash
    python -m data_extractor.main
    ```

The script should now successfully get past this import error and begin the scraping and processing task. We are clearing these structural hurdles one by one.

"""