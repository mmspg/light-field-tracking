import datetime
import os
from enum import Enum

BG_COLOR = "#959595"  # mid-grey
IMG_PATH_PREFIX = "img/"
IMG_FORMAT = "png"
OUTPUT_PATH_PREFIX = "output/"

# Number of images following the current image that are loaded in advance
NB_IMAGES_PRELOADED = 1

# Create an output folder if it doesn't already exist
if not os.path.exists(OUTPUT_PATH_PREFIX):
    os.makedirs(OUTPUT_PATH_PREFIX)

# Open the output files
timestamp = datetime.datetime.now().strftime('%Y.%m.%d-%H.%M.%S')
f_tracking = open(OUTPUT_PATH_PREFIX + timestamp + '-tracking.txt', 'w')
f_answers = open(OUTPUT_PATH_PREFIX + timestamp + '-answers.txt', 'w')

def clamp(x, minimum, maximum):
    """Clamps the value x between a minimum and a maximum."""

    assert (minimum <= maximum)
    return max(minimum, min(maximum, x))

class Helper:
    focus_slider = None
    is_focus_slider_enabled = None

    fullscreen_msg = None

    class Side(Enum):
        LEFT = 0
        RIGHT = 1


