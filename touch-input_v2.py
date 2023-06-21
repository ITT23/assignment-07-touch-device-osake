import cv2
import sys
from os import path
import uuid

CURR_DIR = path.dirname(__file__)
#RECORDINGS_PATH = path.join(CURR_DIR, f"assets/{str(uuid.uuid4())}.mp4")
RECORDED_SESSION_1 = path.join(CURR_DIR, f"assets/cam_video8e2858e0-65a4-4817-bfd6-8034fa781daf.mp4")
RECORDED_SESSION_2 = path.join(CURR_DIR, f"assets/cam_video691bf41f-b9eb-499b-8d32-723a44a10453.mp4")

# needed for the actual case
#video_id = 0

# imitating a webcam
video_1 = cv2.VideoCapture(RECORDED_SESSION_1)
video_2 = cv2.VideoCapture(RECORDED_SESSION_2)

# fps detection
#fps_1 = video_1.get(cv2.CAP_PROP_FPS)
#fps_2 = video_2.get(cv2.CAP_PROP_FPS)

if len(sys.argv) > 1:
    video_id = int(sys.argv[1])

# Create a video capture object for the webcam
cap = cv2.VideoCapture(RECORDED_SESSION_2)

while True:
    # Capture a frame from the webcam
    ret, frame = cap.read()

    # Convert the frame to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    cutoff = 25
    ret, thresh = cv2.threshold(gray, cutoff, 255, cv2.THRESH_BINARY)

    # Display the frame
    cv2.imshow('frame', thresh)

    # Wait for a key press and check if it's the 'q' key
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the video capture object and close all windows
cap.release()
cv2.destroyAllWindows()