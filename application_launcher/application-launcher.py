from argparse import ArgumentParser
import os, time, platform
from enum import Enum
from typing import Union

from pyglet import app, window
from pyglet.shapes import Circle
from pyglet.text import Label
from pyglet.window import key

from DIPPID import SensorUDP
from recognizer import Recogniser, Point

CURR_DIR = os.path.dirname(__file__)


class Font:
  COLOUR = (255,255,255,255)
  INFO = "Open apps according to applications.txt. Templates loaded: "
  NAME = "Verdana"
  TEXT_X = 50
  TEXT_Y = 50
  TEXT_SIZE = 15


class TouchState(Enum):
  NONE = 0
  TOUCH = 1
  DRAG = 2
  RELEASE = 3
  HOVER = 4


class Launcher:

  OS_NAMES = ['Linux', 'Darwin', 'Windows']

  def __init__(self) -> None:
    self.current_platform = platform.system()
    if self.current_platform not in self.OS_NAMES:
      raise Exception("your operating system is not supported by this application")    

  def open_app(self, app_path: str) -> None:
    if not os.path.exists(path=app_path):
      raise Exception(f"there is no application specified with path: {app_path}")

    #LINUX
    if self.current_platform == self.OS_NAMES[0]:
      #for linux, there is no prefix required to open an app from /usr/bin/
      os.system(f"{app_path} &")

    #MACOS
    elif self.current_platform == self.OS_NAMES[1]:
      if not app_path.endswith(".app"):
        raise Exception("macos application must end with .app")
      os.system(f"open {app_path} &")

    #WINDOWS
    #TODO: i dont know how to start applications on windows
    elif self.current_platform == self.OS_NAMES[2]:
      os.system(f"{app_path}")

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
  TOUCH_RELEASE_THRESHOLD = 1 #seconds
  MAX_LEN_DQ = 20
  DEFAULT_POSITION = (0,0)

  def __init__(self, port: int) -> None:
    self._sensor = SensorUDP(port)
    self._sensor.register_callback(self.TOUCH_SCREEN_EVENT_NAME, self._cb)

    self._last_update = time.time()
    self._last_state = TouchState.NONE
    
  def _cb(self, *_) -> None:
    self._last_update = time.time()

  def check_update(self) -> tuple[TouchState, tuple[int, int]]:
    if time.time() - self._last_update > self.TOUCH_RELEASE_THRESHOLD:
      self._last_state = TouchState.RELEASE
      self._last_update = time.time()
      
      return (self._last_state, self.DEFAULT_POSITION)

    data = self._sensor.get_value(self.TOUCH_SCREEN_EVENT_NAME)
    if len(data) == 0:
      self._last_state = TouchState.NONE

      return (self._last_state, self.DEFAULT_POSITION)


    if data["0"]["type"].upper() == TouchState.TOUCH.name or data["0"]["type"].upper() == TouchState.HOVER.name:
      if self._last_state == TouchState.TOUCH or self._last_state == TouchState.DRAG:
        self._last_state = TouchState.DRAG

      else:
        self._last_state = TouchState.TOUCH

      return (self._last_state, (data["0"]["x"], data["0"]["y"]))

    else:
      self._last_state = TouchState.NONE
      self._last_update = time.time()

      return (self._last_state, self.DEFAULT_POSITION)


class Mapping:

  def __init__(self, app_name: str, gesture_name: str) -> None:
    self.app_name = app_name
    self.gesture_name = gesture_name


class Application:

  FPS = 1 / 20
  WIDTH = 1280
  HEIGTH = 720
  NAME = "Application Launcher"

  CURR_DIR = os.path.dirname(__file__)
  TEMPLATE_PATH = os.path.join(CURR_DIR, "templates/")
  MAPPINGS_FILE = os.path.join(CURR_DIR, "applications.txt")

  CIRCLE_COLOUR = (255,0,0,255)
  CIRCLE_RADIUS = 5
  CIRCLE_COLOUR_START = (0,0,255,255)
  CIRCLE_RADIUS_START = 8

  def __init__(self, dippid_port: int) -> None:
    self.window = window.Window(self.WIDTH, self.HEIGTH, caption=self.NAME)
    self.width = self.window.width
    self.height = self.window.height
    self.on_draw = self.window.event(self.on_draw)
    self.on_key_release = self.window.event(self.on_key_release)

    #mouse events
    self.on_mouse_drag = self.window.event(self.on_mouse_drag)
    self.on_mouse_release = self.window.event(self.on_mouse_release)
    self.on_mouse_press = self.window.event(self.on_mouse_press)

    #touch screen events
    self.t_input = TouchscreenInput(dippid_port)
    
    self.mappings = self._load_mappings()

    self.recogniser = Recogniser()
    self.recogniser.load_templates(self.TEMPLATE_PATH, self.mappings)
    self._template_names = self.recogniser.get_unique_template_names()

    self.launcher = Launcher()

    self.shapes: list[Circle] = []
    self.points: list[Point] = []

    self.label = Label(text=Font.INFO, font_name=Font.NAME, font_size=Font.TEXT_SIZE, bold=True, color=Font.COLOUR, x=Font.TEXT_X, y=Font.TEXT_Y)
    self.label.text = self.label.text + ', '.join(self._template_names)

  def _denormalise(self, x: int, y: int) -> tuple[int, int]:
    #also mirroring x values in this step
    new_x = (1 - x) * self.width
    new_y = y * self.height

    return (new_x, new_y)

  def _load_mappings(self) -> list[Mapping]:
    mappings: list[Mapping] = []

    with open(self.MAPPINGS_FILE, "r") as f:
      content = f.read().split("\n")
      
      for line in content:
        gesture_name, app_path = line.split(" ")

        if not os.path.exists(app_path):
          raise Exception(f"path for {app_path} does not exist")

        mappings.append(Mapping(app_path, gesture_name))
    
    return mappings

  def _get_app_by_gesture(self, gesture_name: str) -> Union[str, None]:
    for mapping in self.mappings:
      if mapping.gesture_name == gesture_name:
        return mapping.app_name
    
    return None

  def run(self) -> None:
    app.run()

  def on_draw(self) -> None:
    self.window.clear()
    
    state, coordinates = self.t_input.check_update()
    if state == TouchState.RELEASE:
      self.on_mouse_release() #reusing mouse methods as they have the same body
    elif state == TouchState.TOUCH:
      self.on_mouse_press()
    elif state == TouchState.DRAG:
      x, y = self._denormalise(coordinates[0], coordinates[1])
      self.on_mouse_drag(x, y)
    elif state == TouchState.NONE:
      self.on_mouse_press()

    for point in self.shapes:
      point.draw()

    self.label.draw()

    time.sleep(self.FPS)

  def on_mouse_drag(self, x: int, y: int, *_) -> None:
    #draws the first circle in blue and larger so that the starting points is recognisable
    if len(self.shapes) == 0:
      shape = Circle(x=x, y=y, radius=self.CIRCLE_RADIUS_START, color=self.CIRCLE_COLOUR_START)
    
    else:
      shape = Circle(x=x, y=y, radius=self.CIRCLE_RADIUS, color=self.CIRCLE_COLOUR)

    self.shapes.append(shape)
    self.points.append(Point(x,y))

  def on_mouse_release(self, *_) -> None:
    t1 = time.time()

    template, score = self.recogniser.recognise(self.points)

    if template == None:
      self.label.text = "Too few points drawn."
      return

    mapped_app = self._get_app_by_gesture(template.name)
    if mapped_app == None:
      self.label.text = "Invalid gesture"
      return

    self.launcher.open_app(mapped_app)
    accuracy = format(score, ".2f")
    t_delta = round((time.time() - t1) * 1000)

    self.label.text = f"Result: {template.name} ({accuracy}) in {t_delta}ms."
    
  def on_mouse_press(self, *_) -> None:
    self.shapes = []
    self.points = []

  def on_key_release(self, symbol: int, *_) -> None:
    if symbol == key.ESCAPE:
      app.exit()

    elif symbol == key.Q:
      self.on_mouse_press()


if __name__ == "__main__":
  parser = ArgumentParser(prog=f"{Application.NAME}", description="todo")
  parser.add_argument("-p", default=5700, type=int, help="dippid port")

  args = parser.parse_args()

  application = Application(dippid_port=args.p)

  application.run()