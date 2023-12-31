import cv2
import sys
from os import path
import uuid

CURR_DIR = path.dirname(__file__)
RECORDINGS_PATH = path.join(CURR_DIR, "../assets/gestures/random_hover_and_touch2.mp4")

video_id = 1

if len(sys.argv) > 1:
    video_id = int(sys.argv[1])

# Create a video capture object for the webcam
cap = cv2.VideoCapture(video_id)

vid_cod = cv2.VideoWriter_fourcc(*'XVID')
output = cv2.VideoWriter(RECORDINGS_PATH, vid_cod, 20.0, (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))))

while True:
    # Capture a frame from the webcam
    ret, frame = cap.read()

    # Convert the frame to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Display the frame
    cv2.imshow('frame', frame)
    output.write(frame)

    # Wait for a key press and check if it's the 'q' key
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the video capture object and close all windows
cap.release()
output.release()
cv2.destroyAllWindows()