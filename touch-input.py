'''
ToDo:
- nahebeieinanderliegende areas gruppieren 
- Kalibrierung ausprobieren
  -> Cutoff nachjustieren bis Wert erziehlt wird 
  -> Zu Beginn soll der Kalibrierungsprozess stattfinden (user soll darüber informiert werden)
            -> für cutoff und Lichtverhältnisse
            -> Zwischen light und strong Touch (eventuell über die Größe der Area)


'''

import cv2
import sys
from os import path
import uuid
import time

# webcam id
video_id = 0

if len(sys.argv) > 1:
    video_id = int(sys.argv[1])

# Create a video capture object for the webcam
cap = cv2.VideoCapture(video_id)

cutoff = 25

def touch_areas(img_raw):
    global cutoff
    
    # convert the frame to grayscale img for threshold filter and getting the contours of them
    img_gray = cv2.cvtColor(img_raw, cv2.COLOR_BGR2GRAY)
    
    ret, thresh = cv2.threshold(img_gray, cutoff, 255, cv2.THRESH_BINARY)
    
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # convert back to colored img to see the touch areas
    img_gray = cv2.cvtColor(img_gray, cv2.COLOR_BAYER_BG2BGR)

    # contours of the touched areas
    touch_areas_contours:list = []

    for contour in contours:
        area = cv2.contourArea(contour)
        if area >= 10 and area <= 50:
            (x,y),radius = cv2.minEnclosingCircle(contour)
            center = (int(x),int(y))
            radius = int(radius) * 3
            cv2.circle(img_gray,center,radius,(0,255,0),3)
            touch_areas_contours.append(contour)
    
    if len(touch_areas_contours) > 0:
        print(len(touch_areas_contours))
    
    #img_contours = cv2.cvtColor(img_gray, cv2.COLOR_BGR2RGB)
    img_contours = cv2.drawContours(img_gray, touch_areas_contours, -1, (255, 160, 122), 3)

    return img_contours

while True:
    # Capture a frame from the webcam
    ret, frame = cap.read()

    # get touch areas
    processed_img = touch_areas(frame)

    # Display the frame
    cv2.imshow('frame', processed_img)

    # Wait for a key press and check if it's the 'q' key
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    time.sleep(0.05)

# Release the video capture object and close all windows
cap.release()
cv2.destroyAllWindows()