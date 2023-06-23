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

from collections import deque

# own helper classes
from helper_classes.agglomerative_clustering import Agglomerative_Cluster_Model

CURR_DIR = path.dirname(__file__)
#RECORDINGS_PATH = path.join(CURR_DIR, f"assets/{str(uuid.uuid4())}.mp4")
#RECORDED_SESSION = path.join(CURR_DIR, f"assets/touch_stärker_2.mp4") # Touch
RECORDED_SESSION = path.join(CURR_DIR, f"assets/touch_hover_leichter_2.mp4") # Hover

# area treshholds for touch/hover detection
area_lower_limit = 0
area_upper_limit = 50

# Create a video capture object for the webcam
cap = cv2.VideoCapture(RECORDED_SESSION)

cutoff = 15 # 15 für touch
radius_touch = 40
radus_hover = 60

# dominant fingertip memory
dom_fing_dq:list = deque(maxlen=1)
# current dominant fingertip touch
curr_dom_touch:list = deque(maxlen=1)

aggl_clusterer = Agglomerative_Cluster_Model()


def touch_areas(img_raw):
    global cutoff, dom_fing_dq, curr_dom_touch, radius_touch
    
    # convert the frame to grayscale img for threshold filter and getting the contours of them
    img_gray = cv2.cvtColor(img_raw, cv2.COLOR_BGR2GRAY)
    
    ret, thresh = cv2.threshold(img_gray, cutoff, 255, cv2.THRESH_BINARY)
    
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # convert back to colored img to see the touch areas
    img_bgr = cv2.cvtColor(img_gray, cv2.COLOR_BAYER_BG2BGR)

    # contours of the touched areas
    touch_areas_contours:list = []

    for contour in contours:
        area = cv2.contourArea(contour)
        if area >= area_lower_limit and area <= area_upper_limit:
            #(x,y),radius = cv2.minEnclosingCircle(contour)
            #center = (int(x),int(y))
            #radius = int(radius) * 3
            #cv2.circle(img_gray,center,radius,(0,255,0),3)q
            touch_areas_contours.append(contour)
            
    area_contours_clustered = aggl_clusterer.agglomerative_clustering(touch_areas_contours)
        
    final_areas:list = []
    
    #img_contours = cv2.cvtColor(img_gray, cv2.COLOR_BGR2RGB)
    #img_areas = cv2.drawContours(img_gray, area_contours_clustered, -1, (255, 160, 122), 3)
    
    
    
        #print(dom_fing_dq[0])
    '''
    if len(final_areas) > 0:
        (x,y),radius = cv2.minEnclosingCircle(final_areas[0])
        print((x,y))
        if (int(x), int(y)) in dom_fing_dq:
            print('old position')
            final_areas[0] = curr_dom_touch
        else:
            dom_fing_dq.append((int(x),int(y)))
            curr_dom_touch = final_areas[0]
            #print(dom_fing_dq)
            print('new')
    '''
    
    # Flackern reduzieren
    # old or new position
    if len(area_contours_clustered) > 0:
        (x,y),radius = cv2.minEnclosingCircle(area_contours_clustered[0])
        print((x,y))
        if len(dom_fing_dq) == 0:
            dom_fing_dq.append((x,y))
        if len(curr_dom_touch) == 0:
            curr_dom_touch.append(area_contours_clustered[0])
        x_old, y_old = dom_fing_dq[0]
        if x_old - 50 < x and x_old + 50 > x and y_old - 50 < y and y_old + 50 > y:
            print('old position')
            area_contours_clustered[0] = curr_dom_touch[0]
            print(curr_dom_touch)
        else:
            dom_fing_dq.append((x,y))
            curr_dom_touch.append(area_contours_clustered[0])
            #print(dom_fing_dq)
            print('new')
            
    for contour in area_contours_clustered:
        area = cv2.contourArea(contour)
        
        (x,y),radius = cv2.minEnclosingCircle(contour)
        center = (int(x),int(y))
        radius = radius_touch
        cv2.circle(img_bgr,center,radius,(0,255,0),3)
        final_areas.append(contour)
    
    
        #print(len(final_areas))
    img_areas = cv2.drawContours(img_bgr, final_areas, -1, (255, 160, 122), 3)

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