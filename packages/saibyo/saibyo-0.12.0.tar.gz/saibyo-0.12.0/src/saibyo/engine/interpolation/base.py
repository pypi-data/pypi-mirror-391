from abc import ABC, abstractmethod

import torch


class BaseInterpolationModel(ABC):
    """
    Base class for all interpolation models.
    """

    @abstractmethod
    def load(self, path: str) -> "BaseInterpolationModel": ...  # noqa: D102

    @abstractmethod
    def inference(self) -> torch.Tensor: ...  # noqa: D102
