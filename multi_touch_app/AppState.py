from enum import Enum

class AppState(Enum):
  DEFAULT = 0
  DEBUG = 1

class TouchState(Enum):
  TOUCH = 0
  HOVER = 1
  RELEASE = 2