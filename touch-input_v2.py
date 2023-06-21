import cv2
import sys
from os import path
import uuid
import time

CURR_DIR = path.dirname(__file__)
#RECORDINGS_PATH = path.join(CURR_DIR, f"assets/{str(uuid.uuid4())}.mp4")
RECORDED_SESSION_1 = path.join(CURR_DIR, f"assets/cam_video8e2858e0-65a4-4817-bfd6-8034fa781daf.mp4")
RECORDED_SESSION_2 = path.join(CURR_DIR, f"assets/cam_video691bf41f-b9eb-499b-8d32-723a44a10453.mp4")

# needed for the actual case
#video_id = 0

# imitating a webcam
video_1 = cv2.VideoCapture(RECORDED_SESSION_1)
video_2 = cv2.VideoCapture(RECORDED_SESSION_2)

cutoff = 0

# fps detection
#fps_1 = video_1.get(cv2.CAP_PROP_FPS)
#fps_2 = video_2.get(cv2.CAP_PROP_FPS)

if len(sys.argv) > 1:
    video_id = int(sys.argv[1])

# Create a video capture object for the webcam
cap = cv2.VideoCapture(RECORDED_SESSION_2)

def update(img_gray, threshold=128):
    global cutoff
    
    ret, thresh = cv2.threshold(img_gray, cutoff, 255, cv2.THRESH_BINARY)
    
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    new_contour:list = []

    print(len(contours))

    img_gray = cv2.cvtColor(img_gray, cv2.COLOR_BAYER_BG2BGR)


    for contour in contours:
        area = cv2.contourArea(contour)
        if area >= 2 and area <= 50:
            (x,y),radius = cv2.minEnclosingCircle(contour)
            center = (int(x),int(y))
            radius = int(radius) * 3
            cv2.circle(img_gray,center,radius,(0,255,0),3)
            new_contour.append(contour)

    while len(new_contour) < 3:
        cutoff += 1
    
    if len(new_contour) > 3:
        print('irgendetwas')
    
    #img_contours = cv2.cvtColor(img_gray, cv2.COLOR_BGR2RGB)
    img_contours = cv2.drawContours(img_gray, new_contour, -1, (255, 160, 122), 3)

    return img_contours

while True:
    # Capture a frame from the webcam
    ret, frame = cap.read()

    # Convert the frame to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    #cutoff = 25
    thresh_img = update(gray)
    #ret, thresh = cv2.threshold(gray, cutoff, 255, cv2.THRESH_BINARY)

    # Display the frame
    cv2.imshow('frame', thresh_img)

    # Wait for a key press and check if it's the 'q' key
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    time.sleep(0.05)

# Release the video capture object and close all windows
cap.release()
cv2.destroyAllWindows()