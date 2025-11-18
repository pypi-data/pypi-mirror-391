import logging
from pathlib import Path

from attrs import define, field

from saibyo.conf.conf import SaibyoConf
from saibyo.constants.app import APP_NAME
from saibyo.core.interpolation.interpolator import BaseInterpolator
from saibyo.core.io.video import VideoIOManager
from saibyo.engine.interpolation.engine import RifeEngine
from saibyo.metadata.video import VideoMetadata
from saibyo.utils.interpolation.audio import transfer_audio


@define
class RifeInterpolator(BaseInterpolator):
    """
    Class to interpolate frames using the RIFE model.
    The class is initialized with a configuration object and the device
    to use for inference. The class loads the interpolation model and provides
    a method to run the interpolation on a given input folder containing
    original frames and save the interpolated frames to a given output folder.

    Attributes
    ----------
    _logger : logging.Logger
        The logger object to log messages.
    conf : SaibyoConf
        The configuration object containing the settings for the interpolator.

    """

    conf: SaibyoConf

    _logger: logging.Logger = field(factory=lambda: logging.getLogger(APP_NAME))

    def run(self, input_path: str, output_folder: str) -> "RifeInterpolator":
        """
        Run the interpolator.

        Parameters
        ----------
        input_path : str
            The path to the input video that will be fps boosted using interpolation.
        output_folder : str
            The path to the output folder where the interpolated video will be saved.

        """
        video = VideoMetadata(input_path=input_path)
        video.info()

        multiplier = 2 ** self.conf.interpolator.exponential

        output_path = Path(output_folder)/video.new_name(multiplier)
        Path(output_folder).mkdir(parents=True, exist_ok=True)
        self._logger.info(f"[📂] Output path: {output_path}")

        boosted_fps = video.fps * multiplier
        self._logger.info(
            f"[⚙️] Boosting FPS from {int(video.fps)} to {int(boosted_fps)} using RIFE "
            "model..."
        )

        self._logger.info("[🪶] Loading Interpolation Model.")
        RifeEngine(
            conf=self.conf,
            io_manager=VideoIOManager(
                video=video,
                fps=boosted_fps,
                output_path=str(output_path)
            ),
            total_frames=video.total_frames
        ).run()
        self._logger.info("[✅] Interpolation completed successfully.")

        self._logger.info("[🔊] Transferring audio to the output video.")
        transfer_audio(
            source_video=video.input_path,
            target_video=output_path
        )
        self._logger.info("[✅] Audio transfer completed successfully.")
        self._logger.info(
            f"[📹] Interpolated video saved to: {output_path} with "
            f"{int(boosted_fps)} FPS."
        )

        return self
