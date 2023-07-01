import cv2

class Config:
  # colors for the touch and hover circles (circled bounding boxes)
  COLOR_TOUCH = (255, 0, 0)
  COLOR_HOVER = (0, 128, 0)
  # detection area
  AREA_LOWER_LIMIT = 250
  AREA_UPPER_LIMIT = 2500
  # deviation acceptance for new input
  DEVIATION = 50
  # radius for the touch and hover circles (circled bounding boxes)
  TOUCH_DISPLAY_RADIUS = 20
  HOVER_DISPLAY_RADIUS = 30
  # IP for the DIPPID sender
  IP = "127.0.0.1"
  # amount of stored input detection outcomes till the analysis of the calculated cutoff happens
  # 1 = touch/hover detected (correctly); 0 = touch/hover not detected (correctly)
  CALIBRATION_THRESHOLD = 90
  # amount of needed correct detections to accept the calculated cutoff for touch and hover
  CALIBRATION_THRESHOLD_ACCEPTANCE = int(CALIBRATION_THRESHOLD * 0.9) # 90 percent
  # clustering threshold
  CLUSTERING_THRESHOLD = 40.0
  # max cutoff 
  CUTOFF_LIMIT = 90
  # staring value for the cutoff calibration
  CUTOFF_START = 20

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
  # touch calibration info text 
  START_TOUCH_CALIBRATION_TEXT:list = ["First, the calibration for touch takes place.", "Position your index finger in the middle of the touch display.", \
                                 "The finger should touch the display with the fingertip.", "(clearly distinguishable from hovering)", \
                                  "Then press the 'c' key to start the calibration."]
  # hover calibration info text
  START_HOVER_CALIBRATION_TEXT:list = ["Next, the calibration for hover takes place.", "Position your index finger in the middle of the touch display.", \
                                 "The finger should only touch the display with the fingernail.", "Then press the 'c' key to start the calibration."]
  # hover calibration process text
  HOVER_CALIBRATION_TEXT = "Draw around with your fingernail (maintain contact)."
  # touch calibration process text
  TOUCH_CALIBRATION_TEXT = "Draw around with your fingertip (maintain contact)."