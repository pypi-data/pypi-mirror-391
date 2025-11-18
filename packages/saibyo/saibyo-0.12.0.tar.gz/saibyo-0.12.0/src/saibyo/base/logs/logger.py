import sys
from datetime import datetime, timezone
from logging import DEBUG, INFO, FileHandler, Formatter, StreamHandler, getLogger
from pathlib import Path

from saibyo.base.constants.app import ENV, LOG_ON_FILE


def configure_logging(
    app_name: str, root_dir: str | None = None, logs_folder: str | None = None
) -> None:
    """
    Configure logs for the application. If the environment is "development",
    set the logs level to DEBUG, otherwise is set to INFO. The environment
    is set on the ENV environment variable.

    This service will log on stdout and also into log files. The log files will
    be created on the folder `logs` and will be named `app-<date>.log`. <date>
    is the current date in ISO format, more specifically the time when the
    service started last time.
    """
    if ENV == "test":
        return

    formatter = Formatter(
        "%(asctime)s %(levelname)-8s" + f" {app_name} " + "%(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )
    logger = getLogger(app_name)

    logger.setLevel(INFO)
    if ENV in ["development", "local"]:
        logger.setLevel(DEBUG)

    handler = StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    if not LOG_ON_FILE:
        return

    logs_path = Path(logs_folder)
    if not logs_path.is_absolute() and root_dir is not None:
        logs_path = Path(root_dir) / logs_path

    logs_file = logs_path / f"{datetime.now(tz=timezone.utc).isoformat()}.log"
    logs_path.mkdir(parents=True, exist_ok=True)

    file_handler = FileHandler(logs_file)
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
