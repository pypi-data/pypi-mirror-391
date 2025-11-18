import logging
import os

def setup_logging(log_file="logs/pipeline.log", debug=False):
    """
    Setup logging for the entire TozaText project.
    Always saves to a file; prints to console only if debug=True.
    """
    os.makedirs(os.path.dirname(log_file) or ".", exist_ok=True)

    log_format = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"

    logger = logging.getLogger("preprocessing")
    logger.setLevel(logging.INFO)
    logger.propagate = False  
    
    if not logger.handlers:
        file_handler = logging.FileHandler(log_file, mode="a", encoding="utf-8")
        file_handler.setFormatter(logging.Formatter(log_format))
        logger.addHandler(file_handler)

    # Configure the root logger (affects all submodules)
        if debug:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(logging.Formatter(log_format))
            logger.addHandler(console_handler)

    return logger
