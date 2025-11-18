import os

from pydantic import BaseModel


class App(BaseModel):
    """
    Configuration object for app settings.

    Attributes
    ----------
    logs_folder : str
        Path to the folder where logs will be saved.

    """

    logs_folder: str = os.getenv("LOGS_FOLDER", "/logs")


class Conf(BaseModel):
    """
    Configuration object for application settings.

    Attributes
    ----------
    app : App
        The app configuration object.

    """

    app: App = App()

