from abc import ABC, abstractmethod


class BaseInterpolator(ABC):
    """
    Abstract base class for video frame interpolation.
    This class defines the interface for video frame interpolation models.
    """

    @abstractmethod
    def run(self, input_path: str, output_folder: str) -> "BaseInterpolator": ...  # noqa: D102
