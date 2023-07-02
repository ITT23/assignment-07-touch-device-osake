from enum import Enum

class ActionState(Enum):
  NONE = 0
  HOVER = 1
  TOUCH = 2
  SELECT = 3
  MOVE = 4
  ROTATE = 5
  SCALE = 6