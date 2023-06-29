import time
from typing import Callable

from DIPPID import SensorUDP
from AppState import TouchState

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
  TOUCH_SCREEN_EVENT_NAME = 'touch_screen'
  TOUCH_RELEASE_THRESHOLD = 100 #ms

  def __init__(self, port: int) -> None:
    self._sensor = SensorUDP(port)
    self.callbacks = {}

    self._sensor.register_callback(self.TOUCH_SCREEN_EVENT_NAME, self._cb_touch)
    self._last_update = time.time()
    self._touch_status = TouchState.RELEASE

  def _cb_touch(self, data: dict) -> None:
    if data["event"] == "touch" and self._touch_status == TouchState.TOUCH:
      self.callbacks["drag"](data["x"], data["y"])
    
    elif data["event"] == "touch":
      self.callbacks["on_touch_press"]()
      self._touch_status = TouchState.TOUCH
    
    elif data["event"] == "hover":
      self.callbacks["on_touch_hover"](data["x"], data["y"])
      self._touch_status = TouchState.HOVER

    self._last_update = time.time()
    
  def check_update(self) -> None:
    if time.time() - self._last_update > self.TOUCH_RELEASE_THRESHOLD:
      self.callbacks["on_touch_release"]()
      self._touch_status = TouchState.RELEASE

  def register_callback(self, key: str, cb: Callable) -> None:
    self.callbacks[key] = cb
