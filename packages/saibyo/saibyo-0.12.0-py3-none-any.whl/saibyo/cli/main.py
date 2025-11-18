import fire

from saibyo.cli.compare import compare
from saibyo.cli.interpolate import interpolate


def main() -> None:
    """
    CLI entrypoint.
    """
    fire.Fire({
        "interpolate": interpolate,
        "compare": compare,
    })
