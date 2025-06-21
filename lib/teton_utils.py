import os
import json
import logging
import platform


def load_config():
    """Load OS specific configuration from conf/config.json."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(base_dir, "../conf/config.json")
    with open(config_path, "r") as fh:
        config = json.load(fh)
    return config.get(platform.system(), {})


def load_app_config():
    """Load application configuration from conf/app_config.json."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    app_config_path = os.path.join(base_dir, "../conf/app_config.json")
    with open(app_config_path, "r") as fh:
        return json.load(fh)


def initialize_logging(log_filename="router.log"):
    """Initialize a simple logging setup."""
    logger = logging.getLogger()
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)
    os.makedirs("logs", exist_ok=True)
    file_path = os.path.join("logs", log_filename)
    fh = logging.FileHandler(file_path)
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logger.addHandler(fh)

    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(logging.Formatter("%(asctime)s - %(message)s"))
    logger.addHandler(ch)

    logger.info("Logging initialized.")
    return logger
