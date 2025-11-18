import math
from pathlib import Path
from typing import TYPE_CHECKING

import cv2
import numpy as np

if TYPE_CHECKING:
    from saibyo.metadata.video import VideoMetadata


def frame_at_time(cap: cv2.VideoCapture, time_in_sec: float) -> np.ndarray:
    """
    Retrieves a frame from the video capture object at a specified time in seconds.

    Parameters
    ----------
    cap : cv2.VideoCapture
        The video capture object from which to retrieve the frame.
    time_in_sec : float
        The time in seconds at which to retrieve the frame.

    Returns
    -------
    np.ndarray or None
        The frame at the specified time, or None if the frame could not be retrieved.

    """
    cap.set(cv2.CAP_PROP_POS_MSEC, time_in_sec * 1000)
    ret, frame = cap.read()
    return frame if ret else None

def put_text(
    frame: np.ndarray,
    video_metadata: "VideoMetadata",
    position: str
) -> np.ndarray:
    """
    Adds text overlay to a video frame with video metadata.

    Parameters
    ----------
    frame : np.ndarray
        The video frame to which the text will be added.
    video_metadata : VideoMetadata
        Metadata containing video information such as FPS and input path.
    position : str
        The position where the text will be placed on the frame.
        Supported values are "top_left", "top_right", "bottom_left", and "bottom_right".

    Returns
    -------
    np.ndarray
        The video frame with the text overlay added.

    """
    line1 = f"{math.ceil(video_metadata.fps)} FPS"
    line2 = Path(video_metadata.input_path).name

    thickness = max(1, video_metadata.width // 500)
    font_size = max(0.5, video_metadata.width / 1000)
    font = cv2.FONT_HERSHEY_SIMPLEX
    padding = 10
    line_spacing = int(font_size * 20)  # separación vertical entre líneas

    (w1, h1), _ = cv2.getTextSize(line1, font, font_size, thickness)
    (w2, h2), _ = cv2.getTextSize(line2, font, font_size, thickness)
    text_width = max(w1, w2)
    text_height_total = h1 + h2 + line_spacing

    match position:
        case "top_left":
            x = video_metadata.width // 20
            y = video_metadata.height // 20 + h1
        case "top_right":
            x = video_metadata.width - video_metadata.width // 20 - text_width
            y = video_metadata.height // 20 + h1
        case "bottom_left":
            x = int(video_metadata.width * 0.02)
            y = (
                video_metadata.height - video_metadata.height //
                20 - text_height_total + h1
            )
        case "bottom_right":
            x = int(video_metadata.width * 0.52)
            y = (
                video_metadata.height - video_metadata.height //
                20 - text_height_total + h1
            )
        case _:
            msg = f"Unsupported text position: {position}"
            raise ValueError(msg)

    x1 = max(x - padding, 0)
    y1 = max(y - h1 - padding, 0)
    x2 = min(x + text_width + padding, frame.shape[1])
    y2 = min(y + h2 + line_spacing + padding, frame.shape[0])

    roi = frame[y1:y2, x1:x2].copy()
    cv2.rectangle(roi, (0, 0), (x2 - x1, y2 - y1), (0, 0, 0), thickness=-1)
    blended = cv2.addWeighted(roi, 0.4, frame[y1:y2, x1:x2], 0.6, 0)
    frame[y1:y2, x1:x2] = blended

    cv2.putText(
        frame, line1, (x, y), font, font_size, (255, 255, 255), thickness, cv2.LINE_AA
    )
    cv2.putText(
        frame,
        line2,
        (x, y + h2 + line_spacing),
        font,
        font_size,
        (255, 255, 255),
        thickness,
        cv2.LINE_AA
    )

    return frame
