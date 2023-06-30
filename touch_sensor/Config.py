import cv2

class Config:
  COLOR_TOUCH = (255, 0, 0)
  COLOR_HOVER = (0, 128, 0)
  # detection area
  AREA_LOWER_LIMIT = 250
  AREA_UPPER_LIMIT = 2500
  # deviation acceptance for new input
  DEVIATION = 50

  TOUCH_DISPLAY_RADIUS = 20
  HOVER_DISPLAY_RADIUS = 30

  IP = "127.0.0.1"

  CALIBRATION_THRESHOLD = 100
  CALIBRATION_THRESHOLD_ACCEPTANCE = int(CALIBRATION_THRESHOLD * 0.9)

  # calibration text attributes
    # font
  FONT = cv2.FONT_HERSHEY_SIMPLEX
    # fontScale
  FONT_SCALE_INFO_TXT = 0.5
    # Blue color in BGR
  COLOR_INFO_TXT = (255, 0, 0)
    # Line thickness 
  THICKNESS_INFO_TXT = 1

    # calibration text
  # touch calibration 
  START_TOUCH_CALIBRATION_TEXT:list = ["First, the calibration for touch takes place.", "Position your index finger in the middle of the touch display.", \
                                 "The finger should touch the display with the fingertip.", "(clearly distinguishable from hovering)", \
                                  "Then press the 'c' key to start the calibration."]
  # hover calibration
  START_HOVER_CALIBRATION_TEXT:list = ["Next, the calibration for hover takes place.", "Position your index finger in the middle of the touch display.", \
                                 "The finger should only touch the display with the fingernail.", "Then press the 'c' key to start the calibration."]

  HOVER_CALIBRATION_TEXT = "Draw around with your fingernail (maintain contact)."
  TOUCH_CALIBRATION_TEXT = "Draw around with your fingertip (maintain contact)."