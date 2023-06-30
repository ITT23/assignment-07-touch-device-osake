from enum import Enum

class AppState(Enum):
  DEFAULT = 0
  DEBUG = 1
  CALIBRATION = 2
  CALIBRATION_LOAD = 3

class CalibrationState(Enum):
  HOVER_INFO = 0
  HOVER = 1
  TOUCH_INFO = 3
  TOUCH = 2
  FINISHED = 4

class Interaction(Enum):
  NONE = 0
  HOVER = 1
  TOUCH = 2