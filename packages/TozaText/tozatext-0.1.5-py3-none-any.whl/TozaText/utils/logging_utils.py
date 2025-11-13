import logging
import os

def setup_logging(log_file="logs/pipeline.log", debug=False):
    """
    Setup logging for the entire TozaText project.
    Always saves to a file; prints to console only if debug=True.
    """
    os.makedirs(os.path.dirname(log_file) or ".", exist_ok=True)

    log_format = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"

    file_handler = logging.FileHandler(log_file, mode="w", encoding="utf-8")
    file_handler.setFormatter(logging.Formatter(log_format))

    # Configure the root logger (affects all submodules)
    logging.basicConfig(
        level=logging.INFO,
        handlers=[file_handler],
        format=log_format,
        force=True,  # clears any existing handlers
    )

    # Add optional console output
    if debug:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter(log_format))
        logging.getLogger().addHandler(console_handler)

    logger = logging.getLogger(__name__)  # current module name, not fixed
    return logger
