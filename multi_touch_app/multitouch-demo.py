#load all images in a subdirectory called “img”
# images should be displayed with random size and orientation in a fullscreen pyglet window
#receive DIPPID events from your touch sensor.
#   move images by dragging them with their finger
#   rotate images with a two-finger gesture
#   scale images with a two-finger gesture
#Simultaneous manipulation of multiple images works.

from argparse import ArgumentParser
import os, time

from pyglet import app, window, image
from pyglet.window import key
from pyglet.image import ImageData

from AppState import AppState
from Image import Image

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

  def __init__(self, dippid_port: int, state: AppState) -> None:
    self.state = state
    if self.state == AppState.DEFAULT:
      self.window = window.Window(fullscreen=True, caption=self.NAME)
    else:
      self.window = window.Window(width=self.DEBUG_WIDTH, height=self.DEBUG_HEIGHT, caption=self.NAME)

    self.width = self.window.width
    self.height = self.window.height

    self.on_draw = self.window.event(self.on_draw)
    self.on_key_release = self.window.event(self.on_key_release)

    #mouse events
    self.on_mouse_drag = self.window.event(self.on_mouse_drag)
    self.on_mouse_release = self.window.event(self.on_mouse_release)
    self.on_mouse_press = self.window.event(self.on_mouse_press)

    self.images: list[Image] = []
    self._load_images()
    self._init_image_parameters()
    
  def _load_images(self) -> None:
    if not os.path.exists(self.ASSET_FOLDER) or not os.path.isdir(self.ASSET_FOLDER):
      raise Exception(f"{self.ASSET_FOLDER} is invalid directory")

    for *_, file_names in os.walk(self.ASSET_FOLDER):
      for file_name in file_names:
        image_path = os.path.join(self.ASSET_FOLDER, file_name)

        self.images.append(Image(image_path, (self.width, self.height)))

  def _init_image_parameters(self) -> None:
    pass

  def run(self) -> None:
    app.run()

  def on_draw(self) -> None:
    self.window.clear()

    for image in self.images:
      image.draw()

    time.sleep(self.FPS)

  def on_mouse_drag(self, x: int, y: int, *_) -> None:
    pass

  def on_mouse_release(self, *_) -> None:
    pass
    
  def on_mouse_press(self, *_) -> None:
    pass
  
  def on_touch_hover(self, x: int, y: int, *_) -> None:
    pass

  def on_key_release(self, symbol: int, _) -> None:
    if symbol == key.ESCAPE:
      app.exit()


if __name__ == "__main__":
  parser = ArgumentParser(prog=f"{Application.NAME}", description="todo")
  parser.add_argument("-p", default=5700, type=int, help="dippid port")
  parser.add_argument("-s", default="default", type=str, choices=[state.name.lower() for state in AppState], help="debug mode does not start fullscreen and prints logs.")

  args = parser.parse_args()

  application = Application(dippid_port=args.p, state=AppState[args.s.upper()])

  application.run()