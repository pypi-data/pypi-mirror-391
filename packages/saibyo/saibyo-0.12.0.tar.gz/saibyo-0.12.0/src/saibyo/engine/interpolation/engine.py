import logging

import numpy as np
import torch
import torch.nn.functional as F
from attrs import define, field
from tqdm import tqdm

from saibyo.conf.conf import SaibyoConf
from saibyo.constants.app import APP_NAME, SSIM_0_2, SSIM_0_996, WEIGHTS_DIR
from saibyo.core.io.video import VideoIOManager
from saibyo.engine.interpolation.rife import RifeModel
from saibyo.utils.interpolation.msssim import ssim_matlab


@define
class RifeEngine:
    """
    RIFE interpolation engine for video frame interpolation. This class handles
    the loading of the RIFE model, processing video frames, and performing
    interpolation between frames.

    Attributes
    ----------
    conf : SaibyoConf
        Configuration object containing settings for the interpolation process.
    io_manager : VideoIOManager
        Manager for reading and writing video frames.
    total_frames : int
        Total number of frames in the video to be processed.
    _scale : float
        Scale factor for the interpolation process.
    _logger : logging.Logger
        Logger for logging messages during the interpolation process.
    _device : torch.device
        Device on which the model will run (CPU or GPU).
    _multiplier : int
        Multiplier for the number of interpolated frames to generate between
        each pair of original frames.
    model : RifeModel
        Instance of the RIFE model used for frame interpolation.

    """

    conf: SaibyoConf
    io_manager: VideoIOManager
    total_frames: int

    _scale: float = field(default=1, init=True)
    _logger: logging.Logger = field(
        default=logging.getLogger(APP_NAME), init=True
    )
    _device: torch.device = field(default=torch.device(
        "cuda" if torch.cuda.is_available() else "cpu"), init=True
    )
    _multiplier: int = field(init=False)
    model: RifeModel = field(init=False)

    def __attrs_post_init__(self) -> None:
        """
        Post-initialization method to set up the RIFE model and device
        settings. This method is called automatically after the instance is
        created. It sets the scale factor based on the configuration, enables
        CUDA if available, and loads the RIFE model for frame interpolation.
        """
        torch.set_grad_enabled(False)
        if self.conf.interpolator.lightweight:
            self._logger.info("[🪶] Using lightweight mode")
            torch.set_default_tensor_type(torch.cuda.HalfTensor)

        self._logger.info("[🔍] Loading RIFE model...")
        self._multiplier = 2 ** self.conf.interpolator.exponential
        self.model = RifeModel().load(WEIGHTS_DIR).eval()

    def _make_inference(
        self, image_0: torch.Tensor, image_1: torch.Tensor
    ) -> list[torch.Tensor]:
        return [
            self.model.inference(
                image_0, image_1, (i + 1) * 1.0 / (self._multiplier), self._scale
            )
            for i in range(self._multiplier - 1)
        ]

    def _pad_image(self, image: torch.Tensor, padding: tuple) -> torch.Tensor:
        if(self.conf.interpolator.lightweight):
            return F.pad(image, padding).half()

        return F.pad(image, padding)

    def run(self) -> None:  # noqa: C901, PLR0912, PLR0915
        """
        Run the RIFE interpolation engine to process video frames and generate
        interpolated frames. This method reads frames from the input video,
        performs interpolation using the RIFE model, and writes the output
        frames to the output video file. It handles both static and dynamic
        frames, applying padding as necessary to ensure consistent dimensions
        for the model inference. The method also includes a progress bar to
        track the processing of frames.
        """
        self._logger.info("[🚀] Starting RIFE interpolation...")

        # Initialize variables for frame processing
        lastframe = self.io_manager.read_buffer.get()
        h, w, _ = lastframe.shape

        if self.conf.interpolator.comparation:
            left = w // 4
            w = w // 2

        tmp = max(128, int(128 / self._scale))
        ph = ((h - 1) // tmp + 1) * tmp
        pw = ((w - 1) // tmp + 1) * tmp
        padding = (0, pw - w, 0, ph - h)

        pbar = tqdm(total=self.total_frames)

        if self.conf.interpolator.comparation:
            lastframe = lastframe[:, left: left + w]

        image_1 = torch.from_numpy(np.transpose(lastframe, (2, 0, 1))).to(
            self._device, non_blocking=True
        ).unsqueeze(0).float() / 255.0
        image_1 = self._pad_image(image_1, padding)

        temp: torch.Tensor | None = None

        while True:
            if temp is not None:
                frame = temp
                temp = None
            else:
                frame = self.io_manager.read_buffer.get()
                pbar.update(1)
            if frame is None:
                break

            image_0 = image_1
            image_1 = torch.from_numpy(np.transpose(frame, (2, 0, 1))).to(
                self._device, non_blocking=True
            ).unsqueeze(0).float() / 255.0
            image_1 = self._pad_image(image_1, padding)

            image_0_small, image_1_small = (
                F.interpolate(image_0, (32, 32),
                              mode="bilinear", align_corners=False),
                F.interpolate(image_1, (32, 32),
                              mode="bilinear", align_corners=False)
            )
            ssim = ssim_matlab(image_0_small[:, :3], image_1_small[:, :3])

            break_flag = False
            if ssim > SSIM_0_996:
                frame = self.io_manager.read_buffer.get()
                if frame is None:
                    break_flag = True
                    frame = lastframe
                else:
                    temp = frame
                image_1 = torch.from_numpy(np.transpose(frame, (2, 0, 1))).to(
                    self._device, non_blocking=True
                ).unsqueeze(0).float() / 255.0
                image_1 = self._pad_image(image_1, padding)
                image_1 = self.model.inference(image_0, image_1, scale=self._scale)

                image_1_small = F.interpolate(
                    image_1, (32, 32), mode="bilinear", align_corners=False
                )
                ssim = ssim_matlab(image_0_small[:, :3], image_1_small[:, :3])
                frame = (image_1[0] * 255).byte().cpu().numpy().transpose(
                    1, 2, 0
                )[:h, :w]
                pbar.update(1)

            if ssim < SSIM_0_2:
                output = [image_0 for _ in range(self._multiplier - 1)]
            else:
                output = self._make_inference(image_0, image_1)
            if self.conf.interpolator.comparation:
                self.io_manager.write_buffer.put(
                    np.concatenate((lastframe, lastframe), 1)
                )
                for mid in output:
                    mid_frame = (
                        (mid[0] * 255.).byte().cpu().numpy().transpose(1, 2, 0)
                    )
                    self.io_manager.write_buffer.put(
                        np.concatenate((lastframe, mid_frame[:h, :w]), 1)
                    )
            else:
                self.io_manager.write_buffer.put(lastframe)
                for mid in output:
                    mid_frame = (
                        (mid[0] * 255.).byte().cpu().numpy().transpose(1, 2, 0)
                    )
                    self.io_manager.write_buffer.put(mid_frame[:h, :w])
            lastframe = frame
            if break_flag:
                break
        if self.conf.interpolator.comparation:
            self.io_manager.write_buffer.put(np.concatenate((lastframe, lastframe), 1))
        else:
            self.io_manager.write_buffer.put(lastframe)
        self.io_manager.finish()
        pbar.close()
