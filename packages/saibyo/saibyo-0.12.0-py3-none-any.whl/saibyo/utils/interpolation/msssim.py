from math import exp

import torch
import torch.nn.functional as F


def gaussian(window_size: int, sigma: float) -> torch.Tensor:
    """
    Creates a 1D Gaussian window of the specified size and standard deviation.

    Parameters
    ----------
    window_size : int
        The size of the Gaussian window.
    sigma : float
        The standard deviation of the Gaussian distribution.

    Returns
    -------
    torch.Tensor
        A 1D tensor representing the Gaussian window.

    """
    gauss = torch.Tensor(
        [
            exp(-(x - window_size//2)**2/float(2*sigma**2))
            for x in range(window_size)]
    )
    return gauss/gauss.sum()

def create_window_3d(
        window_size: int, channel: int = 1
) -> torch.Tensor:
    """
    Creates a 3D Gaussian window for SSIM calculation.

    Parameters
    ----------
    window_size : int
        The size of the Gaussian window.
    channel : int, optional
        The number of channels in the input images (default is 1).

    Returns
    -------
    torch.Tensor
        A 3D tensor representing the Gaussian window.

    """
    window_1d = gaussian(window_size, 1.5).unsqueeze(1)
    window_2d = window_1d.mm(window_1d.t())
    window_3d = window_2d.unsqueeze(2) @ (window_1d.t())

    return window_3d.expand(
        1, channel, window_size, window_size, window_size
    ).contiguous()


def ssim_matlab(
        img1: torch.Tensor,
        img2: torch.Tensor,
        window_size: int = 11,
        window: torch.Tensor = None,
        size_average: bool = True,
        val_range: int | None = None
    ) -> torch.Tensor:
    """
    Computes the Structural Similarity Index (SSIM) between two images.

    Parameters
    ----------
    img1 : torch.Tensor
        The first input image tensor of shape (N, C, H, W).
    img2 : torch.Tensor
        The second input image tensor of shape (N, C, H, W).
    window_size : int, optional
        The size of the Gaussian window to use for SSIM calculation (default is 11).
    window : torch.Tensor, optional
        Precomputed Gaussian window tensor. If None, a new window will be created.
    size_average : bool, optional
        If True, the output will be averaged over all dimensions (default is True).
    val_range : int or None, optional
        The value range of the input images. If None, it will be inferred from
        the images

    """
    # Value range can be different from 255. Other common ranges are 1
    # (sigmoid) and 2 (tanh).
    if val_range is None:
        max_val = 255 if torch.max(img1) > 128 else 1  # noqa: PLR2004
        min_val = -1 if torch.min(img1) < -0.5 else 0  # noqa: PLR2004
        l = max_val - min_val  # noqa: E741
    else:
        l = val_range          # noqa: E741

    padd = 0
    (_, _, height, width) = img1.size()
    if window is None:
        real_size = min(window_size, height, width)
        window = create_window_3d(real_size, channel=1).to(img1.device)

    mu1 = F.conv3d(
        F.pad(img1.unsqueeze(1), (5, 5, 5, 5, 5, 5), mode="replicate"),
        window,
        padding=padd,
        groups=1
    )
    mu2 = F.conv3d(
        F.pad(img2.unsqueeze(1), (5, 5, 5, 5, 5, 5), mode="replicate"),
        window,
        padding=padd,
        groups=1
    )

    mu1_sq = mu1.pow(2)
    mu2_sq = mu2.pow(2)
    mu1_mu2 = mu1 * mu2

    sigma1_sq = F.conv3d(
        F.pad(img1 * img1, (5, 5, 5, 5, 5, 5), "replicate"),
        window,
        padding=padd,
        groups=1
    ) - mu1_sq
    sigma2_sq = F.conv3d(
        F.pad(img2 * img2, (5, 5, 5, 5, 5, 5), "replicate"),
        window,
        padding=padd,
        groups=1
    ) - mu2_sq
    sigma12 = F.conv3d(
        F.pad(img1 * img2, (5, 5, 5, 5, 5, 5), "replicate"),
        window,
        padding=padd,
        groups=1
    ) - mu1_mu2

    c1 = (0.01 * l) ** 2
    c2 = (0.03 * l) ** 2

    v1 = 2.0 * sigma12 + c2
    v2 = sigma1_sq + sigma2_sq + c2

    ssim_map = ((2 * mu1_mu2 + c1) * v1) / ((mu1_sq + mu2_sq + c1) * v2)

    return ssim_map.mean() if size_average else ssim_map.mean(1).mean(1).mean(1)


