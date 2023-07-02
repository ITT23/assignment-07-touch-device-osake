import time
from typing import Callable
from collections import deque

from DIPPID import SensorUDP
from ActionState import ActionState
from State import State

class TouchscreenInput:
  #events: press, release, drag, hover
  #(x and y coordinates should be normalized to a value between 0 and 1 with (0, 0) being the top left screen corner)
  #combine get_value and registercallback; track times of callbacks; check in get_value when last update was; trigger release;
  '''
    {'type': 'touch', 'x': float, 'y': float}
    {'type': 'hover', 'x': float, 'y': float}

    event_name: touch_screen
    define update rate!!!
  '''
  TOUCH_SCREEN_EVENT_NAME = 'events'
  TOUCH_RELEASE_THRESHOLD = 100 #ms
  DQ_LENGTH = 10

  def __init__(self, port: int) -> None:
    self._sensor = SensorUDP(port)
    self._sensor.register_callback(self.TOUCH_SCREEN_EVENT_NAME, self._cb_touch)
    
    self.state: deque[State] = deque([], maxlen=self.DQ_LENGTH) #only saves events from dippid and differentiates between hover, touch and none (released)

  def _cb_touch(self, data: dict) -> None:
    #example {"events": {"0": {"x": 0.0671875, "y": 0.12187499999999996, "type": "touch"}, "1": {"x": 0.6525133609771728, "y": 0.3062841415405273, "type": "touch"}}}
    current_state = State()
    current_state.vec_1 = (data["0"]["x"], data["0"]["y"])

    if data["0"]["type"] == "touch":
      current_state.state = ActionState.TOUCH

    elif data["0"]["type"] == "hover":
      current_state.state = ActionState.HOVER

    if hasattr(data, "1"):
      current_state.vec_2 = (data["1"]["x"], data["1"]["y"])
      
    self.state.append(current_state)
    
  def update_state(self) -> State:
    if len(self.state) == 0 or time.time() - self.state[-1].timestamp > self.TOUCH_RELEASE_THRESHOLD:
      current_state = State()
      
      self.state.append(current_state)

      return current_state

    return self.state[-1]

