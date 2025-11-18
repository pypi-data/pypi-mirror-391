import _thread
import logging
import time
from queue import Queue

import cv2

from saibyo.constants.app import APP_NAME
from saibyo.metadata import video


class VideoIOManager:
    """
    A class to manage video input/output operations using threading and queues.
    This class handles reading frames from a video generator and writing them
    to a video file in a separate thread to avoid blocking the main thread.
    """

    _logger: logging.Logger
    write_buffer: Queue
    read_buffer: Queue
    video_out: cv2.VideoWriter

    def __init__(
        self,
        video: video.VideoMetadata,
        fps: float,
        output_path: str
    ) -> None:
        """
        Initialize the VideoIOManager with a video metadata object, output
        path, and set up the necessary queues and video writer.

        Parameters
        ----------
        video : video.VideoMetadata
            An instance of VideoMetadata containing video properties like fps,
            width, and height.
        fps : float
            The frames per second to use for the output video.
        output_path : str
            The path where the output video will be saved.

        """
        self._logger = logging.getLogger(APP_NAME)
        self.write_buffer = Queue(maxsize=500)
        self.read_buffer = Queue(maxsize=500)
        self.video_out = cv2.VideoWriter(
            output_path,
            cv2.VideoWriter_fourcc(*"mp4v"),
            round(fps),
            (video.width, video.height)
        )
        self._start_threads(video.input_path)

    def _start_threads(self, video_path: str) -> None:
        """
        Start the threads for reading frames from the video generator and
        writing them to the output video file using queues to manage the
        flow of data between threads.
        """
        _thread.start_new_thread(self._build_read_buffer, (video_path,))
        _thread.start_new_thread(self._clear_write_buffer, ())

    def _clear_write_buffer(self) -> None:
        """
        Continuously read frames from the write buffer and write them to the
        video output file. This method runs in a separate thread to ensure that
        writing frames does not block the main thread and allows for smooth
        video processing.
        """
        while True:
            item = self.write_buffer.get()
            if item is None:
                break
            self.video_out.write(item[:, :, ::-1])

    def _build_read_buffer(self, video_path: str) -> None:
        """
        Continuously read frames from the video generator and put them into the
        read buffer. This method runs in a separate thread to ensure that
        reading frames does not block the main thread and allows for smooth
        video processing.
        """
        try:
            cap = cv2.VideoCapture(video_path)
            while True:
                success, frame = cap.read()
                if not success:
                    break
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                self.read_buffer.put(frame)
            cap.release()
        except Exception:
            self._logger.exception("Error while reading video frames.")
        self.read_buffer.put(None)

    def finish(self) -> None:
        """
        Signal the end of the video processing by putting a None item in the
        write buffer and waiting for all frames to be written before releasing
        the video output file.
        This method should be called when all frames have been processed to
        ensure that the video file is properly closed and saved.
        """
        self.write_buffer.put(None)
        while not self.write_buffer.empty():
            time.sleep(0.1)
        self.video_out.release()
