
import logging
import inspect
from .handler import SumoHttpHandler


def setup_sumo_logger(http_url: str, module_name: str = None, log_level=logging.INFO):

    if not http_url:
        raise ValueError("HTTP URL is required to initialize Sumo logger")

    if module_name is None:
        # Look for the first frame not in this package
        for frame_info in inspect.stack():
            mod_name = frame_info.frame.f_globals.get("__name__")
            if mod_name and not mod_name.startswith("sumo_logger"):
                module_name = mod_name
                break
        else:
            module_name = "UnknownModule"

    logger = logging.getLogger(module_name)
    logger.setLevel(log_level)

    if not any(isinstance(h, SumoHttpHandler) for h in logger.handlers):
        handler = SumoHttpHandler(http_url)
        logger.addHandler(handler)

    return logger
