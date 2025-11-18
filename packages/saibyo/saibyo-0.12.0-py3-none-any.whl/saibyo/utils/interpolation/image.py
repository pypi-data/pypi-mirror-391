import torch
from torch.nn import functional as F


def pad_to_multiple(
        img: torch.Tensor, multiple: int=64
) -> tuple[torch.Tensor, int, int]:
    """
    Pad the input image tensor to the nearest multiple of the specified value.
    The padding is applied to the right and bottom sides of the image.
    The input image tensor is expected to be in the format of (channels, height,
    width), where channels is the number of color channels (e.g., 3 for RGB).
    The output image tensor will have the same number of channels, but the height
    and width will be padded to the nearest multiple of the specified value.
    The function returns the padded image tensor, as well as the original height
    and width of the image.

    Parameters
    ----------
    img : torch.Tensor
        The input image tensor to be padded.
    multiple : int, optional
        The value to which the height and width of the image should be padded.
        The default value is 64.

    Returns
    -------
    tuple[torch.Tensor, int, int]
        A tuple containing the padded image tensor, the original height, and the
        original width of the image.

    """
    _, h, w = img.shape
    ph = ((h - 1) // multiple + 1) * multiple
    pw = ((w - 1) // multiple + 1) * multiple
    padding = (0, pw - w, 0, ph - h)  # (left, right, top, bottom)
    return F.pad(img, padding), h, w
