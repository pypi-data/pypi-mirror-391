from pathlib import Path

APP_NAME="saibyo-lib"
ROOT_DIR = Path(__file__).parent.parent.parent.parent

#-------- Rife Interpolation Constants ###
WEIGHTS_DIR = (
    Path(__file__).parent.parent /
    "engine" /
    "interpolation" /
    "weights" /
    "flownet.pkl"
)
SSIM_0_996 = 0.996
SSIM_0_2 = 0.2

