from saibyo.base.conf.app import configure
from saibyo.conf.conf import SaibyoConf
from saibyo.constants.app import APP_NAME, ROOT_DIR
from saibyo.core.comparation.comparator import Comparator


def compare(video_a: str, video_b: str, output_path: str) -> None:
    """
    Creates a comparison video between two input videos. The comparison is
    created taking into account the confiration settings from the SaibyoConf.

    Parameters
    ----------
    video_a : str
        The path to the first video file to be compared.
    video_b : str
        The path to the second video file to be compared.
    output_path : str
        The path where the comparison video will be saved.

    """
    conf = configure(APP_NAME, ROOT_DIR, SaibyoConf)

    Comparator(conf.comparator).compare(video_a, video_b, output_path)



