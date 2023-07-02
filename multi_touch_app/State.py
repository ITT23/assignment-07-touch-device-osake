import time

from ActionState import ActionState
from Vector import Vector

class State:
  vec_1: Vector = None
  vec_2: Vector = None
  state = ActionState.NONE
  image_index = -1
  timestamp = time.time()

  def has_two_fingers(self) -> bool:
    return self.vec_2 != None