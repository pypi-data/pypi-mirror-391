# akimgtransmitter/core.py
import cv2
import os
import time

def transmit_image(folder, img, delay=0.01):
    """
    Save one image (frame.png) into `folder`, overwriting previous.
    - folder: directory to store the image
    - img: OpenCV image (numpy array)
    - delay: optional sleep (seconds) after write
    Returns the path of the saved image.
    """
    if not os.path.exists(folder):
        os.makedirs(folder, exist_ok=True)

    filepath = os.path.join(folder, "frame.png")
    # write image (overwrites)
    cv2.imwrite(filepath, img)

    print("Transmitter wrote:", filepath)

    if delay:
        time.sleep(delay)

    return filepath
