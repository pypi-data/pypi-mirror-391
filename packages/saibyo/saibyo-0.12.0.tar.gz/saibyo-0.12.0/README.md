# 📦 Saibyo: Deep Learning Video Frame Interpolation Library

[![CI - Python UV](https://img.shields.io/badge/CI-Python%20UV-blue?logo=githubactions)](https://github.com/alrodsa/saibyo/actions/workflows/python-ci.yml)
[![Codecov](https://codecov.io/gh/alrodsa/saibyo/branch/develop/graph/badge.svg)](https://app.codecov.io/gh/alrodsa/saibyo)
[![Publish](https://img.shields.io/badge/Publish-Package-orange?logo=pypi)](https://github.com/alrodsa/saibyo/actions/workflows/publish.yml)
[![Release](https://img.shields.io/badge/Release-Automated-green?logo=github)](https://github.com/alrodsa/saibyo/actions/workflows/release-please.yml)
[![YouTube Demo](https://img.shields.io/badge/YouTube-Demo-red?logo=youtube)](https://youtu.be/NByIRUQXoUE)

![Demo GIF](assets/gifs/f1-comparation.gif)

> ⚠️ **IMPORTANT:** Above gif could not show the full potential of Saibyo fps boost,
check out the video for a better understanding in the [YouTube Demo](https://youtu.be/NByIRUQXoUE).

## 🧭 Table of Contents

- [🔎 Overview](#🔎-overview)
- [⚙️ Setting up `SaibyoConf` variables](#️-setting-up-saibyoconf-variables)
  - [🧬 Configuration Structure in Code](#-configuration-structure-in-code)
  - [🔧 Configuration Methods](#-configuration-methods)
    - [1️⃣ Using `.conf` files](#1️⃣-using-conf-files)
    - [2️⃣ Using Environment Variables](#2️⃣-using-environment-variables)
- [🚀 Usage: Interpolating Video Frames](#🚀-usage-interpolating-video-frames)
  - [1️⃣ Command-Line Interface (CLI)](#1️⃣-command-line-interface-cli)
  - [2️⃣ Programmatic API Usage](#2️⃣-programmatic-api-usage)

---

## 🔎 Overview

**Saibyo** is a Python library designed to perform video frame interpolation using deep learning techniques. Its primary goal is to enhance the fluidity of videos by generating intermediate frames between existing ones. This is especially useful for applications like:

- 🖼️ Smoothing low-FPS footage
- 🎞️ Creating slow-motion effects
- 🧪 Preprocessing datasets for computer vision tasks
- 📊 Comparing videos side-by-side with different visualization modes

### What Saibyo Does

- Takes a sequence of video frames as input.
- Uses a configurable number of intermediate frames per pair, controlled by the `exp` parameter (e.g., `exp=2` → 3 new frames per pair).
- Outputs an enriched sequence of frames to a specified directory.
- Supports videos side-by-side comparison with various visualization modes.

### Features

- ✅ Easy-to-use CLI and programmatic APIs.
- 🧬 Pydantic-based configuration system via `.conf` files or environment variables.
- ⚙️ Support for batch processing and parallel data loading via `num_workers`.
- 🎨 Multiple comparison modes: `side_by_side`, `top_bottom`, `split_half_vertical`, `split_half_horizontal`.

---

## ⚙️ Setting up `SaibyoConf` variables

Saibyo provides a flexible configuration system powered by **Pydantic Settings**, enabling users to configure interpolation and comparison behavior either through `.conf` files or directly via environment variables.

### 🧬 Configuration Structure in Code

The main configuration model for Saibyo flow is defined in `src/saibyo/conf/conf.py`, the pydantic schema for all Saibyo is defined as follows:

```python
class SaibyoConf(Conf, BaseSettings):
    interpolator: InterpolatorConf = Field(default_factory=InterpolatorConf)
    comparison: ComparisonConf = Field(default_factory=ComparisonConf)

    model_config = SettingsConfigDict(env_prefix="SAIBYO_")
```

#### _Interpolator Configuration_

The configuration model used by Saibyo for interpolation is defined as follows:

```python
    class InterpolatorConf(BaseSettings):
        comparation: bool = Field(default=False, description=COMPARATION_DESCRIPTION)
        lightweight: bool = Field(default=True, description=LIGHTWEIGHT_DESCRIPTION)
        exponential: int = Field(default=2, description=EXPONENTIAL_DESCRIPTION)

        model_config = SettingsConfigDict(
            env_prefix="SAIBYO_INTERPOLATOR_",
            extra="allow"
        )
```

#### _Comparison Configuration_

The configuration model used by Saibyo for video comparison is defined as follows:

```python
    class ComparatorConf(BaseSettings):
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

    class OverlayTextConf(BaseSettings):
        overlay: bool = Field(
            default=True, description=OVERLAY_TEXT_DESCRIPTION
        )
        position: TextPositionType = Field(
            default="top_left", description=TEXT_POSITION_DESCRIPTION
        )

        model_config = SettingsConfigDict(
            env_prefix="SAIBYO_COMPARATOR_OVERLAY_TEXT_"
        )
```

#### _Interpolator Configuration_

The configuration model used by Saibyo for interpolation is defined as follows:

```python
    class InterpolatorConf(BaseSettings):
        comparation: bool = Field(default=False, description=COMPARATION_DESCRIPTION)
        lightweight: bool = Field(default=True, description=LIGHTWEIGHT_DESCRIPTION)
        exponential: int = Field(default=2, description=EXPONENTIAL_DESCRIPTION)

        model_config = SettingsConfigDict(
            env_prefix="SAIBYO_INTERPOLATOR_",
            extra="allow"
        )
```

#### _Comparison Configuration_

The configuration model used by Saibyo for video comparison is defined as follows:

```python
    class ComparatorConf(BaseSettings):
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

    class OverlayTextConf(BaseSettings):
        overlay: bool = Field(
            default=True, description=OVERLAY_TEXT_DESCRIPTION
        )
        position: TextPositionType = Field(
            default="top_left", description=TEXT_POSITION_DESCRIPTION
        )

        model_config = SettingsConfigDict(
            env_prefix="SAIBYO_COMPARATOR_OVERLAY_TEXT_"
        )
```

### 🔧 Configuration Methods

There are **two ways** to configure Saibyo:

#### 1️⃣ Using `.conf` files

You can load configuration from predefined files located in the `conf/` directory:

```
conf/
├── development/
│   └── application.conf
└── production/
    └── application.conf
```

To select which file is used, you must set the environment variable `ENV`:

```bash
export ENV=development
# or
export ENV=production
```

This tells Saibyo to automatically read the corresponding file under `conf/{ENV}/application.conf`.

These files define the configuration block for the interpolator, such as:

```yaml
[interpolator]
comparation=False
lightweight=True
exponential=2

[comparator]
background_color=#100000
mode=side_by_side
text.overlay=True
text.position=bottom_left
comparation=False
lightweight=True
exponential=2

[comparator]
background_color=#100000
mode=side_by_side
text.overlay=True
text.position=bottom_left
```

#### 2️⃣ Using Environment Variables

You can also configure Saibyo directly via environment variables, without relying on `.conf` files. This is ideal for containerized deployments or CI environments.

The `InterpolatorConf` uses the prefix `SAIBYO_INTERPOLATOR_` while the `ComparatorConf` uses `SAIBYO_COMPARATOR_`. The value and the description of each variable are as follows:

| Environment Variable                         | Description                                                                 | Default       |
|----------------------------------------------|-----------------------------------------------------------------------------|---------------|
| `SAIBYO_INTERPOLATOR_COMPARATION`            | If `true`, generates an extra comparison video alongside the interpolated one | `false`       |
| `SAIBYO_INTERPOLATOR_LIGHTWEIGHT`            | If `true`, uses fp16 inference (faster, less memory, slightly lower quality) | `true`        |
| `SAIBYO_INTERPOLATOR_EXPONENTIAL`            | Exponent for FPS multiplier (`2 ** exp`) → `1=×2`, `2=×4`, `3=×8`            | `2`           |
| `SAIBYO_COMPARATOR_BACKGROUND_COLOR`         | Background color in hex (for borders/empty areas in comparison)              | `#000000`     |
| `SAIBYO_COMPARATOR_MODE`                     | Layout mode: `side_by_side`, `top_bottom`, `split_half_vertical`, `split_half_horizontal` | `side_by_side` |
| `SAIBYO_COMPARATOR_OVERLAY_TEXT_OVERLAY`     | If `true`, draws overlay text with FPS & filename                           | `true`        |
| `SAIBYO_COMPARATOR_OVERLAY_TEXT_POSITION`    | Overlay text position: `top_left`, `top_right`, `bottom_left`, `bottom_right` | `top_left`    |

This variables can be set in your shell or in a `.env` file. For example, to set the variables in above table, it can be done as follows:

```bash
export SAIBYO_INTERPOLATOR_COMPARATION=true
export SAIBYO_INTERPOLATOR_LIGHTWEIGHT=true
export SAIBYO_INTERPOLATOR_EXPONENTIAL=2
export SAIBYO_COMPARATOR_BACKGROUND_COLOR=#100000
export SAIBYO_COMPARATOR_MODE=side_by_side
export SAIBYO_COMPARATOR_OVERLAY_TEXT_OVERLAY=true
export SAIBYO_COMPARATOR_OVERLAY_TEXT_POSITION=bottom_left
export SAIBYO_INTERPOLATOR_COMPARATION=true
export SAIBYO_INTERPOLATOR_LIGHTWEIGHT=true
export SAIBYO_INTERPOLATOR_EXPONENTIAL=2
export SAIBYO_COMPARATOR_BACKGROUND_COLOR=#100000
export SAIBYO_COMPARATOR_MODE=side_by_side
export SAIBYO_COMPARATOR_OVERLAY_TEXT_OVERLAY=true
export SAIBYO_COMPARATOR_OVERLAY_TEXT_POSITION=bottom_left
```

> #### 🧠 NOTE: Understanding `exp` (exponent)
>
>The `exp` parameter controls how many frames are interpolated between each original pair:
>
>| `exp` | Interpolated Frames | Final Frame Count (per pair) | Multiplier |
>|-------|---------------------|-------------------------------|------------|
>| 1     | 1                   | 2                             | 2×         |
>| 2     | 3                   | 4                             | 4×         |
>| 3     | 7                   | 8                             | 8×         |
>
>This allows flexible fine-tuning between speed and quality depending on the use case.

## 🚀 Usage

### Interpolating Video Frames

The `interpolate` functionality in Saibyo can be executed in two main ways:

#### 1️⃣ Command-Line Interface (CLI)

Run the interpolation directly using the CLI:

```bash
python main.py interpolate input_path output_folder
```

#### 2️⃣ Programmatic API Usage

Invoke the interpolation in your Python code:

```python
conf = configure(APP_NAME, ROOT_DIR, SaibyoConf)
Interpolator(conf).run(
    input_path=input_path,
    output_folder=output_folder,
)
```
