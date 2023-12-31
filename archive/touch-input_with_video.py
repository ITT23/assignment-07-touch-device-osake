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
from helper_classes.touch_input_classes import Image_Processor, DIPPID_Sender

# for testing purposes with video
CURR_DIR = path.dirname(__file__)
#RECORDED_SESSION = path.join(CURR_DIR, f"assets/touch_stärker_2.mp4") # Touch
RECORDED_SESSION = path.join(CURR_DIR, f"assets/touch_hover_leichter_2.mp4") # Hover

calibration_proc = True # normally true, but since calibration process is yet not integreted its False for testing purposes

image_processor = Image_Processor(1)
dippid_sender = DIPPID_Sender(image_processor)


while True:
    # check if touch or hover happened
    processed_img = image_processor.process_image()

    # TEST: if events are correct
    if image_processor.get_is_touched() or image_processor.get_is_hovered():
        dippid_sender.send_events_message()
    
    # Delete it after calibration process is integrated
    # for the calibration process pyglet is used and this line is not necessary anymore because after calibration we dont show this window
    # just for testing purposes
    if calibration_proc:                                                                                                                        # DELETE AFTER IMPL of calibration
        cv2.imshow('frame', processed_img)

    # Wait for a key press and check if it's the 'q' key
    # just for testing purposes, but later it could init a new calibration process
    if cv2.waitKey(1) & 0xFF == ord('q'):                                                                                                         # DELETE AFTER IMPL of calibration
        break

    #time.sleep(0.05)

# Release the video capture object and close all windows
# for testing purposes
image_processor.cap_release()                                                                                                               # DELETE AFTER IMPL of calibration
cv2.destroyAllWindows()                                                                                                                     # DELETE AFTER IMPL of calibration