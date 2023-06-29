from enum import Enum

from pyglet import image
from PIL import Image as PILImage


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

  #dont move out of the window, must be within the window
  #also watch for scale
  '''
  raw_img = Image.fromarray(img).tobytes()

      top_to_bottom_flag = -1
      bytes_per_row = channels * cols
      pyimg = pyglet.image.ImageData(width=cols, 
                                    height=rows, 
                                    fmt=fmt, 
                                    data=raw_img, 
                                    pitch=top_to_bottom_flag * bytes_per_row)

      return pyimg
  '''
  SCALE_MULTIPLYER = 3 #TODO: change this later
  ROTATION_STEP = 10

  def __init__(self, image_path: str, window_dimensions: tuple[int, int]) -> None:
    self._original_image = PILImage.open(image_path, "r")
    self._original_image = self._original_image.convert('RGBA')

    self._work_image = self._original_image.copy() #so that we can reset the image if needed
    self._draw_image = self._convert_to_pyglet()

    self.x = 0
    self.y = 0

    self.scale(SCALE_DIRECTION.SHRINK)
    self.rotate(ROTATE_DIRECTION.LEFT)
    self.move(50,50)

  def _convert_to_pyglet(self) -> None:
    rows, cols, channels = self._work_image.width, self._work_image.height, 4
    image_data = self._work_image.tobytes()

    pyimg = image.ImageData(width=rows, 
                                  height=cols, 
                                  fmt="RGBA", 
                                  data=image_data, 
                                  pitch=-1 * channels * rows)

    return pyimg

  def move(self, x: int, y: int) -> None:
    self.x = x
    self.y = y

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

  #we want to scale so that the ratio of the image stays intact
  #better work with pinch distance
  def scale(self, scale_direction: SCALE_DIRECTION) -> None:
    current_width, current_height = self._work_image.size

    scale_factor = 1
    if scale_direction == scale_direction.GROW:
      scale_factor = self.SCALE_MULTIPLYER
    else:
      scale_factor = 1 / self.SCALE_MULTIPLYER

    new_dimensions = (int(current_width * scale_factor), int(current_height * scale_factor))

    self._work_image = self._work_image.resize(new_dimensions)
    self._draw_image = self._convert_to_pyglet()

  def draw(self) -> None:
    self._draw_image.blit(self.x, self.y)