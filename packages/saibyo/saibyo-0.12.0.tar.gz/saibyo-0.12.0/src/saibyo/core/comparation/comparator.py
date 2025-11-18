import logging
from dataclasses import dataclass, field

import numpy as np

from saibyo.conf.conf import ComparatorConf
from saibyo.constants.app import APP_NAME
from saibyo.engine.comparation.engine import ComparationEngine
from saibyo.metadata.video import VideoMetadata


@dataclass(frozen=True)
class Comparator:
    """
    Comparator class to handle video comparison using the ComparationEngine.
    It uses the configuration settings from ComparatorConf to perform the comparison.

    Attributes
    ----------
    _conf : ComparatorConf
        Configuration settings for the comparator.
    _logger : logging.Logger
        Logger instance for logging messages.

    """

    _conf: ComparatorConf
    _logger: logging.Logger = field(
        default_factory=lambda: logging.getLogger(APP_NAME)
    )

    def compare(
        self, video_a: str, video_b: str, output_path: str
    ) -> np.ndarray:
        """
        Creates a comparison video between two input videos. The comparison is
        created taking into account the configuration settings from the ComparatorConf.

        Parameters
        ----------
        video_a : str
            The path to the first video file to be compared.
        video_b : str
            The path to the second video file to be compared.
        output_path : str
            The path where the comparison video will be saved.

        """
        self._logger.info(f"Comparing {video_a} and {video_b}...")

        VideoMetadata(input_path=video_a)
        VideoMetadata(input_path=video_b)

        comparation_video = ComparationEngine(self._conf).compare(
            video_a=VideoMetadata(input_path=video_a),
            video_b=VideoMetadata(input_path=video_b),
            output_path=output_path
        )

        # Save the comparison video to the specified output path
        self._logger.info(f"Comparison video saved to {output_path}.")

        return comparation_video

