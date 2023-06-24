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
import sys
import time
import pyglet

from collections import deque
from PIL import Image
from pyglet import shapes

# own helper classes
from helper_classes.touch_input_classes import Image_Processor, DIPPID_Sender

# webcam id
video_id = 1

if len(sys.argv) > 1:
    video_id = int(sys.argv[1])

calibration_proc = False # normally true, but since calibration process is yet not integreted its False for testing purposes

image_processor = Image_Processor(video_id)
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
    if not calibration_proc:                                                                                                                        # DELETE AFTER IMPL of calibration
        cv2.imshow('frame', processed_img)

    # Wait for a key press and check if it's the 'q' key
    # just for testing purposes, but later it could init a new calibration process
    elif cv2.waitKey(1) & 0xFF == ord('q'):                                                                                                         # DELETE AFTER IMPL of calibration
        break

    #time.sleep(0.05)

# Release the video capture object and close all windows
# for testing purposes
image_processor.cap_release()                                                                                                               # DELETE AFTER IMPL of calibration
cv2.destroyAllWindows()                                                                                                                     # DELETE AFTER IMPL of calibration