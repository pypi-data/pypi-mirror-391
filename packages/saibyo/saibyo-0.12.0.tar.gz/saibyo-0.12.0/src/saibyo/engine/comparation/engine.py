import logging
import math
from dataclasses import dataclass, field

import cv2
import numpy as np
from tqdm import tqdm

from saibyo.conf.conf import ComparatorConf
from saibyo.constants.app import APP_NAME
from saibyo.metadata.video import VideoMetadata
from saibyo.modules.comparation.canvas import Canvas
from saibyo.utils.comparation.frame import frame_at_time


@dataclass(frozen=True)
class ComparationEngine:
    """
    A class to handle video comparison using specified configuration settings.

    Attributes
    ----------
    _conf : ComparatorConf
        Configuration settings for the comparison engine.
    _logger : logging.Logger
        Logger instance for logging messages during the comparison process.

    """

    _conf: ComparatorConf
    _logger: logging.Logger = field(
        default_factory=lambda: logging.getLogger(APP_NAME)
    )

    def compare(
        self, video_a: VideoMetadata, video_b: VideoMetadata, output_path: str
    ) -> np.ndarray:
        """
        Compares two videos and creates a composite video with the specified
        comparison mode.

        Parameters
        ----------
        video_a : VideoMetadata
            Metadata for the first video.
        video_b : VideoMetadata
            Metadata for the second video.
        output_path : str
            The path where the output video will be saved.

        Returns
        -------
        np.ndarray
            The composite video frame with the comparison applied.

        """
        video_a.info()
        video_b.info()

        self._logger.info(self._conf.background_color)
        self._logger.info(self._conf.mode)
        self._logger.info(self._conf.text)

        canvas = Canvas.create_canvas(
            video_a=video_a,
            video_b=video_b,
            mode=self._conf.mode,
            background_color=self._conf.background_color
        )
        canvas_height, canvas_width = canvas.shape[:2]

        self._logger.info(f"[🖼️] Canvas created with dimensions: {canvas.shape}")

        target_fps = max(video_a.fps, video_b.fps)
        total_frames = math.ceil(video_a.seconds * target_fps)
        self._logger.info(
            f"Using target FPS: {target_fps}, total frames: {total_frames}"
        )

        cap_a = cv2.VideoCapture(video_a.input_path)
        cap_b = cv2.VideoCapture(video_b.input_path)
        comparation_video = cv2.VideoWriter(
            filename=output_path,
            fourcc=cv2.VideoWriter_fourcc(*"mp4v"),
            fps=target_fps,
            frameSize=(canvas_width, canvas_height)
        )

        for i in tqdm(range(total_frames)):
            timestamp = i / target_fps

            frame_a = frame_at_time(cap_a, timestamp)
            frame_b = frame_at_time(cap_b, timestamp)

            if frame_a is None or frame_b is None:
                self._logger.warning(f"Frame {i} missing at {timestamp:.2f}s")
                continue

            if self._conf.text.overlay:
                frame_a, frame_b = Canvas.add_overlay_text(
                    frame_a=frame_a,
                    frame_b=frame_b,
                    video_a=video_a,
                    video_b=video_b,
                    mode=self._conf.mode
                )

            canvas = Canvas.compose_on_canvas(
                canvas.copy(), frame_a, frame_b, mode=self._conf.mode
            )

            comparation_video.write(canvas)

        cap_a.release()
        cap_b.release()
        comparation_video.release()

        self._logger.info("[✅] Video comparison complete.")

        return canvas
