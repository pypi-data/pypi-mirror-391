import shutil
import subprocess
from pathlib import Path


def transfer_audio(source_video: str | Path, target_video: str | Path) -> None:
    """
    Transfers audio from the source video to the target video. If lossless
    transfer fails, attempts to transcode the audio to AAC.

    Parameters
    ----------
    source_video : str or Path
        Path to the original video containing audio.
    target_video : str or Path
        Path to the video file to which the audio should be added.

    """
    source_video = Path(source_video)
    target_video = Path(target_video)
    temp_dir = Path(".tmp")
    temp_dir.mkdir(exist_ok=True)

    audio_stem = target_video.stem
    temp_audio = temp_dir / f"{audio_stem}.mkv"

    # Clean and recreate temp directory
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
        temp_dir.mkdir()

    # Extract audio
    subprocess.run(
        [
            "/usr/bin/ffmpeg",
            "-y",
            "-i",
            str(source_video),
            "-c:a",
            "copy",
            "-vn",
            str(temp_audio),
        ],
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    # Rename target video to _noaudio
    target_no_audio = target_video.with_name(
        f"{target_video.stem}_noaudio{target_video.suffix}"
    )
    target_video.rename(target_no_audio)

    # Try to combine audio + video
    subprocess.run(
        [
            "/usr/bin/ffmpeg",
            "-y",
            "-i",
            str(target_no_audio),
            "-i",
            str(temp_audio),
            "-c",
            "copy",
            str(target_video),
        ],
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    # Fallback to AAC if failed
    if target_video.stat().st_size == 0:
        temp_audio = temp_dir / f"{audio_stem}.m4a"
        subprocess.run(
            [
                "/usr/bin/ffmpeg",
                "-y",
                "-i",
                str(source_video),
                "-c:a",
                "aac",
                "-b:a",
                "160k",
                "-vn",
                str(temp_audio),
            ],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        subprocess.run(
            [
                "/usr/bin/ffmpeg",
                "-y",
                "-i",
                str(target_no_audio),
                "-i",
                str(temp_audio),
                "-c",
                "copy",
                str(target_video),
            ],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        if target_video.stat().st_size == 0:
            target_no_audio.rename(target_video)
            print("Audio transfer failed. Interpolated video will have no audio.")
        else:
            print(
                "Lossless audio transfer failed. Audio was transcoded to AAC (M4A)"
                " instead."
            )
            target_no_audio.unlink()
    else:
        target_no_audio.unlink()

    shutil.rmtree(temp_dir)
