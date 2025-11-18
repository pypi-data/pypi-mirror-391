from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from saibyo.base.conf.schema import Conf
from saibyo.constants.conf import (
    BACKGROUND_COLOR_DESCRIPTION,
    COMPARATION_DESCRIPTION,
    EXPONENTIAL_DESCRIPTION,
    LIGHTWEIGHT_DESCRIPTION,
    MODE_DESCRIPTION,
    OVERLAY_TEXT_DESCRIPTION,
    TEXT_POSITION_DESCRIPTION,
    ModeType,
    TextPositionType,
)


class InterpolatorConf(BaseSettings):
    """
    Configuration for the Interpolator.

    Attributes
    ----------
    comparation : bool
        If True, creates an extra video that compares the original video with the
        interpolated video, showing the differences between them.
    lightweight : bool
        If True, the model inference will be performed using fp16 precision,
        which is faster and uses less memory, but may result in lower quality output.
    exponential : int
        The value of the exponential parameter is used to determine the value of the
        fps multiplier, which is calculated as 2 ** exponential. For example:
        - If exponential is 1, the fps multiplier is 2 ** 1 = 2, resulting in
        double the frames.
        - If exponential is 2, the fps multiplier is 2 ** 2 = 4, resulting in
        quadruple the frames.
        - If exponential is 3, the fps multiplier is 2 ** 3 = 8, resulting in
        eight times the frames.
        This allows for flexible control over the frame rate increase during
        interpolation.

    """

    comparation: bool = Field(default=False, description=COMPARATION_DESCRIPTION)
    lightweight: bool = Field(default=True, description=LIGHTWEIGHT_DESCRIPTION)
    exponential: int = Field(default=2, description=EXPONENTIAL_DESCRIPTION)

    model_config = SettingsConfigDict(
        env_prefix="SAIBYO_INTERPOLATOR_",
        extra="allow"
    )

class OverlayTextConf(BaseSettings):
    """
    Configuration for the Overlay Text.

    Attributes
    ----------
    overlay_text : bool
        If True, displays an overlay with video source info (e.g., FPS, name).

    """

    overlay: bool = Field(
        default=True, description=OVERLAY_TEXT_DESCRIPTION
    )
    position: TextPositionType = Field(
        default="top_left", description=TEXT_POSITION_DESCRIPTION
    )

    model_config = SettingsConfigDict(
        env_prefix="SAIBYO_COMPARATOR_OVERLAY_TEXT_"
    )

class ComparatorConf(BaseSettings):
    """
    Configuration for the Comparator.

    Attributes
    ----------
    text_conf : OverlayTextConf
        Configuration for the overlay text in the comparison video.
    background_color : str
        Background color for borders or empty areas in the comparison video.
    mode : ModeType
        Layout for video comparison, can be either 'side_by_side', 'top_bottom',
        'split_half_vertical', or 'split_half_horizontal'.

    """

    text: OverlayTextConf = Field(
        default_factory=OverlayTextConf
    )
    background_color: str = Field(
        default="#000000",
        description=BACKGROUND_COLOR_DESCRIPTION
    )
    mode: ModeType = Field(
        default="side_by_side",
        description=MODE_DESCRIPTION
    )

    model_config = SettingsConfigDict(
        env_prefix="SAIBYO_COMPARATOR_",
        extra="allow"
    )

class SaibyoConf(Conf, BaseSettings):
    """
    Configuration for the Saibyo application.

    Attributes
    ----------
    interpolator : InterpolatorConf
        Configuration for the interpolator.

    """

    interpolator: InterpolatorConf= Field(default_factory=InterpolatorConf)
    comparator: ComparatorConf = Field(default_factory=ComparatorConf)

    model_config = SettingsConfigDict(env_prefix="SAIBYO_")
