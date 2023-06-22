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
from os import path
import uuid
import time
import numpy as np

# webcam id
video_id = 1

if len(sys.argv) > 1:
    video_id = int(sys.argv[1])

# Create a video capture object for the webcam
cap = cv2.VideoCapture(video_id)

cutoff = 25

# Agglomerative Clustering
# https://cullensun.medium.com/agglomerative-clustering-for-opencv-contours-cd74719b678e
def calculate_contour_distance(contour1, contour2): 
    x1, y1, w1, h1 = cv2.boundingRect(contour1)
    c_x1 = x1 + w1/2
    c_y1 = y1 + h1/2

    x2, y2, w2, h2 = cv2.boundingRect(contour2)
    c_x2 = x2 + w2/2
    c_y2 = y2 + h2/2

    return max(abs(c_x1 - c_x2) - (w1 + w2)/2, abs(c_y1 - c_y2) - (h1 + h2)/2)

# Agglomerative Clustering
# https://cullensun.medium.com/agglomerative-clustering-for-opencv-contours-cd74719b678e
def merge_contours(contour1, contour2):
    return np.concatenate((contour1, contour2), axis=0)

# Agglomerative Clustering
# https://cullensun.medium.com/agglomerative-clustering-for-opencv-contours-cd74719b678e
def agglomerative_cluster(contours, threshold_distance=40.0):
    current_contours = contours
    while len(current_contours) > 1:
        min_distance = None
        min_coordinate = None

        for x in range(len(current_contours)-1):
            for y in range(x+1, len(current_contours)):
                distance = calculate_contour_distance(current_contours[x], current_contours[y])
                if min_distance is None:
                    min_distance = distance
                    min_coordinate = (x, y)
                elif distance < min_distance:
                    min_distance = distance
                    min_coordinate = (x, y)

        if min_distance < threshold_distance:
            index1, index2 = min_coordinate
            current_contours[index1] = merge_contours(current_contours[index1], current_contours[index2])
            del current_contours[index2]
        else: 
            break

    return current_contours


def touch_areas(img_raw):
    global cutoff, threshold_area
    
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
            #(x,y),radius = cv2.minEnclosingCircle(contour)
            #center = (int(x),int(y))
            #radius = int(radius) * 3
            #cv2.circle(img_gray,center,radius,(0,255,0),3)
            touch_areas_contours.append(contour)
            
    area_contours_clustered = agglomerative_cluster(touch_areas_contours)
        
    final_areas:list = []
    
    #img_contours = cv2.cvtColor(img_gray, cv2.COLOR_BGR2RGB)
    #img_areas = cv2.drawContours(img_gray, area_contours_clustered, -1, (255, 160, 122), 3)
    for contour in area_contours_clustered:
        area = cv2.contourArea(contour)
        
        (x,y),radius = cv2.minEnclosingCircle(contour)
        center = (int(x),int(y))
        radius = int(radius) * 2
        cv2.circle(img_gray,center,radius,(0,255,0),3)
        final_areas.append(contour)
        print(len(final_areas))
    img_areas = cv2.drawContours(img_gray, final_areas, -1, (255, 160, 122), 3)

    return img_areas

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

    #time.sleep(0.05)

# Release the video capture object and close all windows
cap.release()
cv2.destroyAllWindows()