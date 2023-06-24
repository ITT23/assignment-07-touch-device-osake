'''
ToDo:
- nahebeieinanderliegende areas gruppieren 
- Kalibrierung ausprobieren
  -> Cutoff nachjustieren bis Wert erziehlt wird 
  -> Zu Beginn soll der Kalibrierungsprozess stattfinden (user soll darüber informiert werden)
            -> für cutoff und Lichtverhältnisse
            -> Zwischen light und strong Touch (eventuell über die Größe der Area)
- Flickern reduzieren (letzte Zustände speichern)


'''

import cv2
from os import path
import time
import pyglet

from collections import deque
from PIL import Image
from pyglet import shapes

# own helper classes
from helper_classes.agglomerative_clustering_class import Agglomerative_Cluster_Model
from helper_classes.touch_input_classes import Image_Processor, DIPPID_Sender

# for testing purposes with video
CURR_DIR = path.dirname(__file__)
#RECORDINGS_PATH = path.join(CURR_DIR, f"assets/{str(uuid.uuid4())}.mp4")
#RECORDED_SESSION = path.join(CURR_DIR, f"assets/touch_stärker_2.mp4") # Touch
RECORDED_SESSION = path.join(CURR_DIR, f"assets/touch_hover_leichter_2.mp4") # Hover

calibration_proc = True

image_processor = Image_Processor(RECORDED_SESSION)
dippid_sender = DIPPID_Sender(image_processor)


while True:
    # check if touch happened
    processed_img = image_processor.process_image()
    if image_processor.get_is_touched() or image_processor.get_is_hovered():
        dippid_sender.get_events_message()
    
    if calibration_proc:
        cv2.imshow('frame', processed_img)

    # Wait for a key press and check if it's the 'q' key
    if cv2.waitKey(1) & 0xFF == ord('c'):
        if calibration_proc:
            calibration_proc = True
        else:
            calibration_proc = False
    elif cv2.waitKey(1) & 0xFF == ord('q'):
        break

    #time.sleep(0.05)

# Release the video capture object and close all windows
image_processor.cap_release()
cv2.destroyAllWindows()
print('connection lost')