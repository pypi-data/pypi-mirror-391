from saibyo.base.conf.app import configure
from saibyo.conf.conf import SaibyoConf
from saibyo.constants.app import APP_NAME, ROOT_DIR
from saibyo.core.interpolation.rife import RifeInterpolator


def interpolate(input_path: str, output_folder: str) -> None:
    """
    Interpolates the data in the input folder and saves it to the output folder.

    Parameters
    ----------
    input_path : str
        The path of the input video that will be fps boosted using interpolation.
    output_folder : str
        The path to the output folder where the interpolated video will be saved.

    """
    conf = configure(APP_NAME, ROOT_DIR, SaibyoConf)

    RifeInterpolator(conf).run(
        input_path=input_path,
        output_folder=output_folder,
    )

