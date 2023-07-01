# different states needed for the application

from enum import Enum

# different states of the application
class AppState(Enum):
  # use touch application without calibration 
  # last calibration values stored in calibration.txt are used
  DEFAULT = 0
  # debug / developer mode
  DEBUG = 1
  # start touch application with the calibration process
  CALIBRATION = 2

# different states of the calibration process
class CalibrationState(Enum):
  # informations for the user about the hover calibration process
  HOVER_INFO = 0
  # hover calibration process
  HOVER = 1
  # informations for the user about the touch calibration process
  TOUCH_INFO = 3
  # touch calibration process
  TOUCH = 2
  # calibration is finished
  FINISHED = 4

# possible interactions (user input outcome)
class Interaction(Enum):
  # neither touch nor hover were detected
  NONE = 0
  # hover(s) was/were detected
  HOVER = 1
  # touch(es) was/were detected
  TOUCH = 2