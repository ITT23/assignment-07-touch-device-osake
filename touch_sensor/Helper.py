import socket, json
import cv2
import numpy as np
import pyglet

from PIL import Image
from cv2 import Mat
from Clustering import Clustering
from AppState import AppState, Interaction
from Config import Config
from typing import Union


# convert cv2 image format to pyglet image format
## https://gist.github.com/nkymut/1cb40ea6ae4de0cf9ded7332f1ca0d55
def cv2glet(img: Mat, fmt: str) -> pyglet.image.ImageData:
    '''Assumes image is in BGR color space. Returns a pyimg object'''
    if fmt == 'GRAY':
      rows, cols = img.shape
      channels = 1

    else:
      rows, cols, channels = img.shape

    raw_img = Image.fromarray(img).tobytes()

    top_to_bottom_flag = -1
    bytes_per_row = channels * cols
    pyimg = pyglet.image.ImageData(width=cols, 
                                   height=rows, 
                                   fmt=fmt, 
                                   data=raw_img, 
                                   pitch=top_to_bottom_flag * bytes_per_row)

    return pyimg


def normalise_points(points: tuple, dimensions: tuple) -> tuple[float, float]:
  '''
    subtract y-axis from 1 so that point of origin is in the top left corner 
  '''
  return (points[0] / dimensions[0], 1 - (points[1] / dimensions[1]))


class Capture:
  
  def __init__(self, video_path: str, video_id: int) -> None:
    if video_path is not None:
      self.capture = cv2.VideoCapture(video_path)

    else:
      self.capture = cv2.VideoCapture(video_id)
    
    if not self.capture.isOpened():
      raise Exception("error opening video stream")

    self.width = int(self.capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    self.height = int(self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT))

  def next_image(self) -> Union[bool, Mat]:
    return self.capture.read()

  def show_frame(self, frame) -> None:
    cv2.imshow('frame', frame)

  def release(self) -> None:
    self.capture.release()


class Output:

  def __init__(self) -> None:
    self.interaction = Interaction.NONE
    self.num_finger = 0
    self.coordinates = []

  def to_json(self) -> str:
    event = {
      "events": {
      }
    }
    
    x, y = self.coordinates[0]

    if self.num_finger == 1: #probably unnessecary because function will not be called when finger == 0
      event["events"]["0"] = {}
      event["events"]["0"]["x"] = x
      event["events"]["0"]["y"] = y
        
      if self.interaction == Interaction.TOUCH:
        event["events"]["0"]["type"] = Interaction.TOUCH.name.lower()

      else:
        event["events"]["0"]["type"] = Interaction.HOVER.name.lower()

    if self.num_finger == 2:
      x_2, y_2 = self.coordinates[1]

      event["events"]["0"] = {}
      event["events"]["0"]["x"] = x
      event["events"]["0"]["y"] = y

      event["events"]["1"] = {}
      event["events"]["1"]["x"] = x_2
      event["events"]["1"]["y"] = y_2
        
      if self.interaction == Interaction.TOUCH:
        event["events"]["0"]["type"] = Interaction.TOUCH.name.lower()

        event["events"]["1"]["type"] = Interaction.TOUCH.name.lower()

      else:
        event["events"]["0"]["type"] = Interaction.HOVER.name.lower()

        event["events"]["1"]["type"] = Interaction.HOVER.name.lower()
  
    return json.dumps(event)


class Image_Processor:

  KERNEL_SIZE = 20
  CUTOFF = 45
  MAX_BOXES = 2
  TOUCH_HOVER_CUTOFF = 850

  def __init__(self, video_dimensions: tuple, calibration: dict):
    self.frame = None
    self._video_dimensions = video_dimensions
    self.touch_radius = video_dimensions[0] // Config.TOUCH_DISPLAY_RADIUS
    self.hover_radius = video_dimensions[0] // Config.HOVER_DISPLAY_RADIUS
    # is input a touch or hover or none
    self.interaction = Interaction.NONE
    # cutoffs for touch and hover
    self.cutoff_touch = int(calibration["CUTOFF_TOUCH"])
    self.cutoff_hover = int(calibration["CUTOFF_HOVER"])
    # used to cluster contour points in order to get the inputs
    self.clustering = Clustering()
    # last coordinates for the input points
    self.last_fing_tip_coordinates: list(tuple) = []
    # current dominant fingertip touch
    self.curr_dom_touch: list = []
    # amount of input points 
    self.points_number = 0 # if 1 finger is touching/hovering it becomes 1 and with 2 fingers it becomes 2 //better use enum?

  # processes image whether it is touch or hover
  # returned image is cv2 format
  def process_image(self, frame: Mat) -> tuple[bool, Mat, Output]:
    # convert the frame to grayscale img for threshold filter and getting the contours of them
    img_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    #dilate->erode=>closes the gamp between areas -> fewer contours
    kernel = np.ones((self.KERNEL_SIZE, self.KERNEL_SIZE), np.uint8)
    edges_img = cv2.dilate(img_gray, kernel)
    edges_img = cv2.erode(edges_img, kernel)
    
    # analyse thresh of image regarding touch and hover
    _, thresh_touch = cv2.threshold(edges_img, self.cutoff_touch, 255, cv2.THRESH_BINARY)
    _, thresh_hover = cv2.threshold(edges_img, self.cutoff_hover, 255, cv2.THRESH_BINARY)
    # get contours for hover and touch (if available)
    contours_touch, _ = cv2.findContours(thresh_touch, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours_hover, _ = cv2.findContours(thresh_hover, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    # check if it was a touch or hover and adjust corresponding values
    self.set_input_status(contours_touch, contours_hover)

    if self.interaction == Interaction.TOUCH:
      bounding_circle_radius = self.touch_radius
      bounding_circle_color = Config.COLOR_TOUCH
      area_contours_clustered = self.get_clustered_points(contours_touch)

    else:
      bounding_circle_radius = self.hover_radius
      bounding_circle_color = Config.COLOR_HOVER
      area_contours_clustered = self.get_clustered_points(contours_hover)

    # convert back to colored img to see the touch areas
    img_bgr = cv2.cvtColor(img_gray, cv2.COLOR_BAYER_BG2BGR)

    final_areas: list = []
  
    # draw the bounding circles into the image
    for contour in area_contours_clustered:
      (x, y), radius = cv2.minEnclosingCircle(contour)
      center = (int(x), int(y))
      radius = bounding_circle_radius
      cv2.circle(img_bgr, center, radius, bounding_circle_color, 3)

      final_areas.append(contour)

    img_bgr = cv2.drawContours(img_bgr, final_areas, -1, (255, 160, 122), 3)
    #flipping the image on the vertical axis so that (0,0) is in the top left corner
    flipped_image = cv2.flip(img_bgr, 0)
    # need for the calibration process (pyglet)
    self.frame = flipped_image

    output = Output()
    output.interaction = self.interaction
    output.num_finger = self.points_number
    for finger in self.last_fing_tip_coordinates:
      output.coordinates.append(normalise_points(finger, self._video_dimensions))

    return (output.interaction is not Interaction.NONE, flipped_image, output)

  # check on the basis of the contours for touch and hover if the input is hovering or touching
  def set_input_status(self, contours_touch: list, contours_hover: list) -> None:
    if len(contours_touch) > 1:
      self.interaction = Interaction.TOUCH

    elif len(contours_hover) > 1:
      self.interaction = Interaction.HOVER
    
    else:
      self.interaction = Interaction.NONE

  # agglomerative clustering of the contour points
  def get_clustered_points(self, contours: list) -> list:
    # contours of the touched areas
    touch_areas_contours: list = []

    for contour in contours:
      area = cv2.contourArea(contour)
      if area >= Config.AREA_LOWER_LIMIT and area <= Config.AREA_UPPER_LIMIT:
        touch_areas_contours.append(contour)
            
    area_contours_clustered = self.clustering.cluster(touch_areas_contours)

    if len(area_contours_clustered) > 2:
      filtered_arr_cluster = []
      filtered_arr_cluster.append(area_contours_clustered[0])
      filtered_arr_cluster.append(area_contours_clustered[1])
      area_contours_clustered = filtered_arr_cluster
        
    # Flackern reduzieren
    # old or new position
    if len(area_contours_clustered) > 0:
      if not self.curr_dom_touch:
        self.curr_dom_touch.append(area_contours_clustered[0])
      
      for i in range(len(area_contours_clustered)):
        (x, y), _ = cv2.minEnclosingCircle(area_contours_clustered[i])
        
        if not self.last_fing_tip_coordinates:
          self.last_fing_tip_coordinates.append((x,y))
          self.last_fing_tip_coordinates.append((x,y))
        
        x_old, y_old = self.last_fing_tip_coordinates[i]
        
        if x_old - Config.DEVIATION < x and x_old + Config.DEVIATION > x and y_old - Config.DEVIATION < y and y_old + Config.DEVIATION > y:
          area_contours_clustered[0] = self.curr_dom_touch[0]
        
        else:
          self.last_fing_tip_coordinates[i] = (x,y)
          self.curr_dom_touch[0] = area_contours_clustered[0]
    
    self.points_number = len(area_contours_clustered)

    return area_contours_clustered
  
  def get_pyglet_image(self):
        img = None
        if self.frame is not None:
            img = cv2glet(self.frame, 'BGR')
        return img 
  
class Calibration:
  
  def __init__(self, image_processor:Image_Processor):
    self.image_handler = image_processor
    
  def draw(self):
        self.image_handler.process_image()
        img = self.image_handler.get
        if img is not None:
            img.blit(0,0,0)
    

class DIPPID_Sender:

  def __init__(self, dippid_port: int):
    self._port = dippid_port
    self._ip = Config.IP
    self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

  def send_event(self, output: Output, app_state: AppState):
    if app_state == AppState.DEBUG:
      print(output.to_json())

    else:
      self._socket.sendto(output.to_json().encode(), (self._ip, self._port))
