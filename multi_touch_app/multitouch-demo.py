#load all images in a subdirectory called “img”
# images should be displayed with random size and orientation in a fullscreen pyglet window
#receive DIPPID events from your touch sensor.
#   move images by dragging them with their finger
#   rotate images with a two-finger gesture
#   scale images with a two-finger gesture
#Simultaneous manipulation of multiple images works.

from argparse import ArgumentParser
import os, time
from collections import deque

from pyglet import app, window
from pyglet.window import key
from pyglet.shapes import Circle

from Image import Image
from TouchInput import TouchscreenInput
from State import State
from ActionState import ActionState

CURR_DIR = os.path.dirname(__file__)


class Font:
  COLOUR = (255,255,255,255)
  INFO = "Open apps according to applications.txt. Templates loaded: "
  NAME = "Verdana"
  TEXT_X = 50
  TEXT_Y = 50
  TEXT_SIZE = 15


class Application:

  FPS = 1 / 60
  DEBUG_WIDTH = 1280
  DEBUG_HEIGHT = 720
  NAME = "Multitouch Demo"

  CURR_DIR = os.path.dirname(__file__)
  ASSET_FOLDER = os.path.join(CURR_DIR, "..", "img")

  DEFAULT_HOVER_POSITION = (-5, -5)
  HOVER_RADIUS = 5
  HOVER_COLOUR = (0,255,0,255)

  DQ_LENGTH = 10

  def __init__(self, dippid_port: int, debug: bool) -> None:
    self.debug = debug
    if self.debug:
      self.window = window.Window(width=self.DEBUG_WIDTH, height=self.DEBUG_HEIGHT, caption=self.NAME)
    else:
      self.window = window.Window(fullscreen=True, caption=self.NAME)

    self.width = self.window.width
    self.height = self.window.height

    self.on_draw = self.window.event(self.on_draw)
    self.on_key_release = self.window.event(self.on_key_release)

    self.hover_circle = Circle(x=self.DEFAULT_HOVER_POSITION[0], y=self.DEFAULT_HOVER_POSITION[1], radius=self.HOVER_RADIUS, color=self.HOVER_COLOUR)

    self.images: list[Image] = []
    self._load_images()

    self.touch_input = TouchscreenInput(dippid_port)
    self.state: deque[State] = deque([], maxlen=self.DQ_LENGTH) #saves action, last position and currently used image
    
  def _load_images(self) -> None:
    if not os.path.exists(self.ASSET_FOLDER) or not os.path.isdir(self.ASSET_FOLDER):
      raise Exception(f"{self.ASSET_FOLDER} is invalid directory")

    for *_, file_names in os.walk(self.ASSET_FOLDER):
      for key, file_name in enumerate(file_names):
        image_path = os.path.join(self.ASSET_FOLDER, file_name)

        self.images.append(Image(key, image_path, (self.width, self.height)))

  def run(self) -> None:
    app.run()

  def on_draw(self) -> None:
    self.window.clear()

    current_state = self.touch_input.update_state()
    self.state.append(current_state.copy())
    current_state = self.state[-1]

    #move and select work interchangeably

    #check if 1 or 2 finger
    if current_state.has_two_fingers():
      x, y = current_state.vec_1.x, current_state.vec_1.y
      #need fixed image from select or move
      #rotate and scale can interchange
      #calc angle -> if angle is less then 2-3 degree -> no rotate
      #calc distance -> if distance greater than x -> scale
      #rotate and scale need at least one finger in the picture
      pass
    else:
      if current_state.state == ActionState.TOUCH:

      #select
        #if previous state has hover or none AND current has touch -> select
        #select image !!!!!!!! can only be checked if there is a previous state!!!!!
        #forward/backward images
        #bounding box

      #move
        #if previous state is select, this 
        pass
      

      if current_state.state == ActionState.HOVER:
        self.hover_circle.x = self.DEFAULT_HOVER_POSITION[0]
        self.hover_circle.y =  self.DEFAULT_HOVER_POSITION[1]



    #unlock image
    #last image is null
    #calculate current

    for image in self.images:
      image.draw()
    self.hover_circle.draw()

    time.sleep(self.FPS)

  def on_key_release(self, symbol: int, _) -> None:
    if symbol == key.ESCAPE:
      self.touch_input.end()
      app.exit()


if __name__ == "__main__":
  parser = ArgumentParser(prog=f"{Application.NAME}", description="todo")
  parser.add_argument("-p", default=5700, type=int, help="dippid port")
  parser.add_argument("-s", default=False, type=bool, help="enter debug mode by passing -s True")

  args = parser.parse_args()

  application = Application(dippid_port=args.p, debug=args.s)

  application.run()