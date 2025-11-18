import configparser
import logging
import os
from pathlib import Path

from saibyo.base.conf.schema import Conf
from saibyo.base.constants.app import ENV, ENVIRONMENTS
from saibyo.base.logs.logger import configure_logging


def configure(app_name: str, root_dir: str, schema: type[Conf] = Conf) -> Conf:
    """
    Configures the app.

    It will read the configuration file from the
    folder `conf/<ENV>/application.conf`. <ENV> is an environment variable
    that can be set to one of the following values:

     - production
     - preview
     - local
     - test
     - development

    If the environment variable `APP_CONFIGURATION_FILE` is set, it will be used
    as the configuration file instead of the previous one.

    This function will validate the configuration file and return a
    configuration object.

    Parameters
    ----------
    app_name : str
        The name of the application.
    root_dir : Path
        The root directory of the application.
    schema : Conf
        The schema used as definition of the configuration file.

    Returns
    -------
    Conf
        The configuration object

    """
    logger = logging.getLogger(app_name)
    root_path = Path(root_dir)

    if ENV not in ENVIRONMENTS:
        message = f"Invalid ENV: {ENV}. It must be one of {ENVIRONMENTS}"
        raise ValueError(message)

    configuration_file = os.getenv("APP_CONFIGURATION_FILE", None)
    if not configuration_file:
        configuration_file = root_path / f"conf/{ENV}/application.conf"
    configuration = configparser.ConfigParser()
    configuration.read(configuration_file)

    schema_dict = configuration._sections  # noqa: SLF001
    if not isinstance(schema_dict, dict):
        schema_dict = schema_dict()

    configuration_instance = schema.model_validate(schema_dict)
    configure_logging(app_name, root_dir, configuration_instance.app.logs_folder)
    logger.info(f"Configuration from {configuration_file}: {configuration_instance}")

    return configuration_instance

