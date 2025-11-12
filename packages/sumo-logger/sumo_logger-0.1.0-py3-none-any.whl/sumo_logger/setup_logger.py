import logging
from .handler import SumoHttpHandler


def setup_sumo_logger(http_url: str, logger_name: str = "SumoLogger", log_level=logging.INFO):
    """
    Creates and configures a logger that sends logs to a Sumo Logic HTTP Source.
    """
    if not http_url:
        raise ValueError("HTTP URL is required to initialize Sumo logger")

    logger = logging.getLogger(logger_name)
    logger.setLevel(log_level)

    if not any(isinstance(h, SumoHttpHandler) for h in logger.handlers):
        handler = SumoHttpHandler(http_url)
        logger.addHandler(handler)

    return logger
