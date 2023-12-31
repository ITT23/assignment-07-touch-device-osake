# helper classes for the main applications
# capture class, image processing class, dippid sender class

import socket, json
import cv2
import numpy as np
import pyglet
import os

from PIL import Image
from cv2 import Mat
from Clustering import Clustering
from AppState import AppState, Interaction, CalibrationState
from Config import Config
from typing import Union
from collections import deque


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

# normalise calculated x and y coordinates of the detected touch/hover
def normalise_points(points: tuple, dimensions: tuple) -> tuple[float, float]:
  '''
    subtract y-axis from 1 so that point of origin is in the top left corner 
  '''
  return (points[0] / dimensions[0], 1 - (points[1] / dimensions[1]))

# cam capture class
class Capture:
  
  def __init__(self, video_path: str, video_id: int) -> None:
    if video_path is not None:
      self.capture = cv2.VideoCapture(video_path)

    else:
      self.capture = cv2.VideoCapture(video_id)
    
    if not self.capture.isOpened():
      raise Exception("error opening video stream")
    
    self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 620)
    self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 440)

    self.width = int(self.capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    self.height = int(self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
    

  def next_image(self) -> Union[bool, Mat]:
    return self.capture.read()

  def show_frame(self, frame) -> None:
    cv2.imshow('frame', frame)

  def release(self) -> None:
    self.capture.release()

# converts output to dippid-ready data
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

    if self.num_finger == 1: #probably unnessecary because function will not be called when finger == 0
      x, y = self.coordinates[0]

      event["events"]["0"] = {}
      event["events"]["0"]["x"] = x
      event["events"]["0"]["y"] = y
        
      if self.interaction == Interaction.TOUCH:
        event["events"]["0"]["type"] = Interaction.TOUCH.name.lower()

      else:
        event["events"]["0"]["type"] = Interaction.HOVER.name.lower()

    if self.num_finger == 2:
      x, y = self.coordinates[0]
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

# process frames regarding wheter it is touch(es)/hover(s)
class Image_Processor:

  KERNEL_SIZE = 20
  MAX_BOXES = 2

  def __init__(self, video_dimensions: tuple):
    self.frame = None
    self.state = None
    self._video_dimensions = video_dimensions
    self.touch_radius = video_dimensions[0] // Config.TOUCH_DISPLAY_RADIUS
    self.hover_radius = video_dimensions[0] // Config.HOVER_DISPLAY_RADIUS
    # is input a touch or hover or none
    self.interaction = Interaction.NONE
    # used to cluster contour points in order to get the inputs
    self.clustering = Clustering()
    # last coordinates for the input points
    self.last_fing_tip_coordinates: list(tuple) = []
    # last (max 5) user inputs data are stored here
    # used to smooth the visualisation of the circled bounding boxes
    self.last_actions = deque([None])
    # current dominant fingertip touch
    self.curr_dom_touch: list = []
    # amount of input points 
    self.points_number = 0 # if 1 finger is touching/hovering it becomes 1 and with 2 fingers it becomes 2 //better use enum?
    # cutoffs get adjusted by the calibration process
    self.cutoff_hover = Config.CUTOFF_START
    self.cutoff_touch = Config.CUTOFF_START
  
  # methods for the calibration process
  def apply_calibration_cutoff(self, calibration:dict):
    self.cutoff_touch = int(calibration["CUTOFF_TOUCH"])
    self.cutoff_hover = int(calibration["CUTOFF_HOVER"])
  
  def get_cutoff_hover(self):
    return self.cutoff_hover
  
  def get_cutoff_touch(self):
    return self.cutoff_touch
  
  def increase_cutoff(self, input_state:str):
    if input_state == "touch":
      self.cutoff_touch += 1
    else:
      self.cutoff_hover += 1

  def decrease_cutoff(self, input_state:str):
    if input_state == "touch":
      self.cutoff_touch -= 1
    else:
      self.cutoff_hover -= 1

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
      # circled bbox attributes for touch
      bounding_circle_radius = self.touch_radius
      bounding_circle_color = Config.COLOR_TOUCH
      # cluster detected contours
      area_contours_clustered = self.get_clustered_points(contours_touch)
      # save input data to smooth out the circled bounding box visualisation
      # don't do it for the calibration process
      if self.state == None:
        self.last_actions.append(area_contours_clustered)
        self.pop_last_actions()

    elif self.interaction == Interaction.HOVER:
      # circled bbox attributes for hover
      bounding_circle_radius = self.hover_radius
      bounding_circle_color = Config.COLOR_HOVER
      # cluster detected contours
      area_contours_clustered = self.get_clustered_points(contours_hover)
      # save input data to smooth out the circled bounding box visualisation
      # don't do it for the calibration process
      if self.state == None:
        self.last_actions.append(area_contours_clustered)
        self.pop_last_actions()

    # no interaction is detected
    else:
      bounding_circle_radius = self.hover_radius
      bounding_circle_color = Config.COLOR_HOVER
      # decide based on the (max 5) last inputs if it is still a interaction which wasn't detected correctly
      # or if it is clearly not a interaction
      if self.state == None:
        self.last_actions.append(None)
        self.pop_last_actions()
        if self.last_actions[0] is not None:
          area_contours_clustered = self.last_actions[0]
        else:
          area_contours_clustered = self.get_clustered_points(contours_hover)
      else:
        area_contours_clustered = self.get_clustered_points(contours_hover)
      

    # convert back to colored img to see the touch areas
    img_bgr = cv2.cvtColor(img_gray, cv2.COLOR_BAYER_BG2BGR)

    # clustered touch/hover points
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

    return (output.interaction is not Interaction.NONE and self.points_number > 0, flipped_image, output)

  # check on the basis of the contours for touch and hover if the input is hover, touch or none of both
  def set_input_status(self, contours_touch: list, contours_hover: list) -> None:
    # touch
    if len(contours_touch) > 1:
      self.interaction = Interaction.TOUCH
    # hover
    elif len(contours_hover) > 1:
      self.interaction = Interaction.HOVER
    # none
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

    # just work with the 2 biggest clusters 
    # since in our usecases with just work with 2 fingers max
    if len(area_contours_clustered) > 2:
      filtered_arr_cluster = []
      filtered_arr_cluster.append(area_contours_clustered[0])
      filtered_arr_cluster.append(area_contours_clustered[1])
      area_contours_clustered = filtered_arr_cluster
        
    # reduce flicker of the circled bboxes 
    # based wheter the input is a old or new finger position
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

    # 1 or 2 fingers used
    self.points_number = len(area_contours_clustered)

    return area_contours_clustered
  
  def get_pyglet_image(self):
        img = None
        if self.frame is not None:
            img = cv2glet(self.frame, 'BGR')
        return img 
  
  def pop_last_actions(self):
    if len(self.last_actions) >= 5:
          self.last_actions.popleft()
  
class Calibration:
  
  def __init__(self, capture:Capture, image_proc:Image_Processor):
    self.window_width = capture.width
    self.window_height = capture.height
    self.image_processor = image_proc
    self.active = False
    self.info_txt_pos = ()
    self.state = CalibrationState.HOVER_INFO
    self.detection_outcome:list = [] # 1 = sucess, 0 = failure
  
  # init or finish the calibration process
  def set_status(self):
    if self.active:
      self.active = False
      self.state = CalibrationState.FINISHED
    else:
      self.active = True
      self.state = CalibrationState.TOUCH_INFO

  # If no finger was detected, the associated cutoff value is increased by 1. The result is stored in the detection_outcome array. 
  # If the finger is recognized and no more than 1 finger is recognized, the value 1 is added to the array. Otherwise 0 and the respective cutoff is reduced by 1. 
  # After 90 evaluated images it is checked whether 81 (90 percent) times the correct recognition was made.
  # if cutoff is higher than 90 -> reset it to 20 and restart this part of the calibration process (case: user lifts its finger or is out of the camera view)
  def calibrate_cutoff(self):
    if self.state == CalibrationState.HOVER or self.state == CalibrationState.TOUCH:

      if self.image_processor.interaction == Interaction.NONE:

        if self.state == CalibrationState.TOUCH:

          self.image_processor.increase_cutoff("touch")

        if self.state == CalibrationState.HOVER:
          
          self.image_processor.increase_cutoff("hover")
          
        self.detection_outcome.append(0)

      else:

        if self.image_processor.points_number > 1:

          if self.state == CalibrationState.TOUCH:
            self.image_processor.decrease_cutoff("touch")
          else:
            self.image_processor.decrease_cutoff("hover")
        
        if self.state.value == self.image_processor.interaction.value and self.image_processor.points_number == 1:
          self.detection_outcome.append(1)
        
        if self.image_processor.cutoff_touch >= Config.CUTOFF_LIMIT or self.image_processor.cutoff_hover >= Config.CUTOFF_LIMIT:

          if self.state == CalibrationState.TOUCH:
            self.image_processor.cutoff_touch = Config.CUTOFF_START
          else:
            self.image_processor.cutoff_hover = Config.CUTOFF_START
          self.detection_outcome = []
        
      if len(self.detection_outcome) >= Config.CALIBRATION_THRESHOLD: # 90
        if self.detection_outcome.count(1) >= Config.CALIBRATION_THRESHOLD_ACCEPTANCE: # 81
          if self.state == CalibrationState.TOUCH:
            self.image_processor.state = None
            self.state = CalibrationState.HOVER_INFO
            self.detection_outcome = []
           
          if self.state == CalibrationState.HOVER:
            self.state = CalibrationState.FINISHED
            self.image_processor.state = None
            self.detection_outcome = []
            self.active = False
            self.save_calibration_data()

        else:
          self.detection_outcome = []

  def save_calibration_data(self):
    CURR_DIR = os.path.dirname(__file__)
    CALIBRATION_FILE = os.path.join(CURR_DIR, "calibration.txt")

    with open('calibration.txt', 'w') as f:
      f.write('CUTOFF_TOUCH ' + str(self.image_processor.cutoff_touch))
      f.write('\n')
      f.write('CUTOFF_HOVER ' + str(self.image_processor.cutoff_hover))

  #https://www.appsloveworld.com/opencv/100/3/how-to-resize-text-for-cv2-puttext-according-to-the-image-size-in-opencv-python
  def get_optimal_font_scale(self, text):
    fontScale = 3*(self.window_width//6)
    for scale in reversed(range(0, 60, 1)):
        textSize = cv2.getTextSize(text, fontFace=cv2.FONT_HERSHEY_DUPLEX, fontScale=scale/10, thickness=1)
        new_width = textSize[0][0]
        if (new_width <= fontScale):
            return scale/7
    return 1

  # info text shown in the calibration process
  def set_info_txt(self, image:Image):
    if self.state is CalibrationState.HOVER_INFO or self.state is CalibrationState.TOUCH_INFO:
      if self.state is CalibrationState.HOVER_INFO:
        info_text_arr:list = Config.START_HOVER_CALIBRATION_TEXT
        font_scale = self.get_optimal_font_scale(Config.START_HOVER_CALIBRATION_TEXT[1])
      else:
        info_text_arr:list = Config.START_TOUCH_CALIBRATION_TEXT
        font_scale = self.get_optimal_font_scale(Config.START_TOUCH_CALIBRATION_TEXT[1])
      
      for i in range(len(info_text_arr)):
        processed_img = cv2.putText(image, info_text_arr[i], (int(self.window_width * 0.2), int(self.window_height * (0.3 + 0.1 * i))), \
                                    Config.FONT, font_scale, Config.COLOR_INFO_TXT, \
                                      Config.THICKNESS_INFO_TXT, cv2.LINE_AA)
    elif self.state is CalibrationState.HOVER:
      processed_img = cv2.putText(image, Config.HOVER_CALIBRATION_TEXT, (int(self.window_width * 0.1), int(self.window_height * 0.1)), Config.FONT, \
                                  self.get_optimal_font_scale(Config.HOVER_CALIBRATION_TEXT), Config.COLOR_INFO_TXT, Config.THICKNESS_INFO_TXT, cv2.LINE_AA)
    elif self.state is CalibrationState.TOUCH:
      processed_img = cv2.putText(image, Config.TOUCH_CALIBRATION_TEXT, (int(self.window_width * 0.1), int(self.window_height * 0.1)), Config.FONT, \
                                  self.get_optimal_font_scale(Config.TOUCH_CALIBRATION_TEXT), Config.COLOR_INFO_TXT, Config.THICKNESS_INFO_TXT, cv2.LINE_AA)
    
    return processed_img

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
      print(output.to_json())
