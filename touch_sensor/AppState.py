from enum import Enum

class AppState(Enum):
  DEFAULT = 0
  DEBUG = 1
  CALIBRATION = 2

class CalibrationState(Enum):
  HOVER_INFO = 0
  HOVER = 1
  TOUCH_INFO = 2
  TOUCH = 3
  FINISHED = 4

class Interaction(Enum):
  NONE = 0
  HOVER = 1
  TOUCH = 2