import logging
import math
from functools import cached_property
from pathlib import Path

import cv2
from attrs import define, field

from saibyo.constants.app import APP_NAME


@define
class VideoMetadata:
    """
    Class to handle video metadata extraction using OpenCV.

    Attributes:
    ----------
    input_path : str
        Path to the input video file.

    Example:
    -------
    >>> video = VideoMetadata(input_path="/path/to/video.mp4")
    >>> print(
    >>>     f"Video FPS: {video.fps}, Total Frames: {video.total_frames}, ",
    >>>     f"Height: {video.height}, Width: {video.width}
    >>> )
    >>> # Video FPS: 30.0, Total Frames: 300, Height: 720, Width: 1280

    """

    input_path: str

    _logger: logging.Logger = field(
        default=logging.getLogger(APP_NAME), init=True
    )

    def __attrs_post_init__(self) -> None:
        """
        Post-initialization method to check if the input path is valid.
        Raises an error if the input path does not exist or is not a file.
        """
        if not Path(self.input_path).exists():
            self._logger.error(f"Input path '{self.input_path}' does not exist.")
            msg = "Input path does not exist."
            raise FileNotFoundError(msg)
        if not Path(self.input_path).is_file():
            self._logger.error(f"Input path '{self.input_path}' is not a valid file.")
            msg = "Input path is not a valid file."
            raise ValueError(msg)

    @cached_property
    def cap(self) -> cv2.VideoCapture:
        """Create a video capture object for the input video."""
        return cv2.VideoCapture(self.input_path)

    @cached_property
    def fps(self) -> float:
        """Get the frames per second of the video."""
        return self.cap.get(cv2.CAP_PROP_FPS)

    @cached_property
    def total_frames(self) -> int:
        """Get the total number of frames in the video."""
        return int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))

    @cached_property
    def height(self) -> int:
        """Get the height of the video."""
        return int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    @cached_property
    def width(self) -> int:
        """Get the width of the video."""
        return int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))

    @cached_property
    def duration(self) -> float:
        """
        Get the duration of the video in HH:MM:SS format.

        Returns
        -------
        str
            The duration of the video formatted as HH:MM:SS.

        """
        total_seconds = self.total_frames / self.fps
        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        seconds = int(total_seconds % 60)
        return f"{hours:02}:{minutes:02}:{seconds:02}"

    @cached_property
    def seconds(self) -> float:
        """
        Get the duration of the video in seconds.

        Returns
        -------
        float
            The duration of the video in seconds.

        """
        return self.total_frames / self.fps

    def __del__(self) -> None:
        """Release the video capture object."""
        if self.cap.isOpened():
            self.cap.release()

    def info(self) -> None:
        """
        Prints the video metadata through the logger.
        """
        self._logger.info(
            f"[🎥] Video Metadata: "
            f"Video FPS: {math.ceil(self.fps)}, Total Frames: {self.total_frames}, "
            f"Height: {self.height}, Width: {self.width}, Duration: {self.duration}"
        )

    def new_name(self, multiplier: int) -> str:
        """
        Generate a new name for the video file based on the multiplier and fps.

        Parameters
        ----------
        multiplier : int
            The multiplier used for interpolation. This indicates how many times
            the original video fps is multiplied.

        Returns
        -------
        str
            The new name for the video file.

        """
        path = Path(self.input_path)
        return f"{path.stem}_x{multiplier}_{int(self.fps * multiplier)}fps{path.suffix}"

