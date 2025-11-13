# akimgreceiver/core.py
import cv2
import os
import time

def receive_image(folder, delay=0.01):
    filepath = os.path.join(folder, "frame.png")

    while True:
        if os.path.exists(filepath):
            img = cv2.imread(filepath)

            if img is not None:
                # delete after reading
                try:
                    os.remove(filepath)
                except:
                    pass

                time.sleep(delay)
                return img

        time.sleep(delay)
