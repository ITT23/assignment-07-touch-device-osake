from enum import Enum

class AppState(Enum):
  DEFAULT = 0
  DEBUG = 1
  CALIBRATION = 2

class Interaction(Enum):
  NONE = 0
  HOVER = 1
  TOUCH = 2