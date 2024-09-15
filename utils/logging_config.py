import logging
import sys

def setup_logging():
    # Get the root logger
    logger = logging.getLogger()
    
    # Check if handlers are already set (avoid duplicates)
    if not logger.hasHandlers():
        # Set global logging level
        logger.setLevel(logging.DEBUG)
        
        # Create and configure console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # Optionally, add a file handler
        # file_handler = logging.FileHandler('app.log')
        # file_handler.setLevel(logging.ERROR)
        # file_handler.setFormatter(formatter)
        # logger.addHandler(file_handler)
    
    # Set logging level for specific libraries
    logging.getLogger('colormath').setLevel(logging.ERROR)
    logging.getLogger('matplotlib').setLevel(logging.ERROR)
    logging.getLogger('PIL').setLevel(logging.WARNING)  # Suppress PIL logs
    logging.getLogger('numba').setLevel(logging.WARNING)  # Suppress numba logs
