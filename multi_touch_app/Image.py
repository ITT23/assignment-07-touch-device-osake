from enum import Enum
import math

from pyglet import image, sprite

from Config import Config
from Vector import Vector


class SCALE_DIRECTION(Enum):
  GROW = 0
  KEEP = 1
  SHRINK = 2


class ROTATE_DIRECTION(Enum):
  LEFT = 0
  KEEP = 1
  RIGHT = 2


class Image:

  #   move images by dragging them with their finger
  #   rotate images with a two-finger gesture
  #   scale images with a two-finger gesture

  def __init__(self, index: int, image_path: str, window_dimensions: tuple[int, int]) -> None:
    self._index = index
    self._window_dimensions = window_dimensions
    self._image_data = image.load(image_path)
    self._image = sprite.Sprite(self._image_data, 0,0,0)
    
    self.init_positions()

    self._last_distance = 1

  def init_positions(self) -> None:
    self._image.x = Config.IMAGE[self._index]["x"] * self._window_dimensions[0]
    self._image.y = Config.IMAGE[self._index]["y"] * self._window_dimensions[1]
    self._image.z = 1
    self._image.rotation = Config.IMAGE[self._index]["rotation"]
    self._image.scale = (self._window_dimensions[0] * Config.IMAGE[self._index]["scale"]) / self._image.width

  def move(self, new_position: Vector) -> None:
    self._image.x = new_position.x
    self._image.y = new_position.y

  #better work with rotation distance?
  def rotate(self, rotate_direction: ROTATE_DIRECTION) -> None:
    '''
      if rotation is negative, image is rotated clockwise
      if rotation is positive, image is rotated counter-clockwise
    '''
    rotation = 1
    if rotate_direction == ROTATE_DIRECTION.LEFT:
      rotation = self.ROTATION_STEP
    else:
      rotation = -1 * self.ROTATION_STEP

    self._work_image = self._work_image.rotate(rotation, expand=True)
    self._draw_image = self._convert_to_pyglet()

  #call when a gesture is over so that scaling works correctly
  def reset_last_distance(self) -> None:
    self._last_distance = 1

  #we want to scale so that the ratio of the image stays intact
  #better work with pinch distance
  def scale(self, main_finger: Vector, help_finger: Vector) -> None:
    #scale image by double of distance
    dy = (main_finger.y - help_finger.y)
    dx = (main_finger.x - help_finger.x)
    distance_fingers = math.sqrt(dy ** 2 + dx ** 2 )

    diff_last_distance = distance_fingers - self._last_distance
    self._last_distance = distance_fingers

    #double scale because pintching normally only considers in one direction?
    self._image.scale = diff_last_distance * 2
    #scale
    #move to main finger = mid
    #because scaling starts from (0,0) we must adjust the midpoint
    self._image.x = self._image.x - self._image.width / 2
    self._image.y = self._image.y - self._image.height / 2

  def check_collision(self, finger: Vector) -> bool:
    pass

  def to_front(self) -> None:
    self._image.z = 2

  def to_back(self) -> None:
    self._image.z = 1

  def draw(self) -> None:
    self._image.draw()