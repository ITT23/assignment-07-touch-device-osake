import cv2
import pyglet

from PIL import Image
from pyglet import shapes

#from collections import deque

# own helper classes
from helper_classes.agglomerative_clustering_class import Agglomerative_Cluster_Model

# radius of bounding circles (bbox)
RADIUS_TOUCH = 50
RADIUS_HOVER = 30
# color of bounding circles (bbox)
COLOR_TOUCH = (255, 0, 0)
COLOR_HOVER = (0, 128, 0)
# detection area
AREA_LOWER_LIMIT = 0
AREA_UPPER_LIMIT = 50
# deviation acceptance for new input
DEVIATION = 50


## https://gist.github.com/nkymut/1cb40ea6ae4de0cf9ded7332f1ca0d55
def cv2glet(img,fmt):
    '''Assumes image is in BGR color space. Returns a pyimg object'''
    if fmt == 'GRAY':
      rows, cols = img.shape
      channels = 1
    else:
      rows, cols, channels = img.shape

    raw_img = Image.fromarray(img).tobytes()

    top_to_bottom_flag = -1
    bytes_per_row = channels*cols
    pyimg = pyglet.image.ImageData(width=cols, 
                                   height=rows, 
                                   fmt=fmt, 
                                   data=raw_img, 
                                   pitch=top_to_bottom_flag*bytes_per_row)
    return pyimg

class Image_Processor:
    def __init__(self, camera_id):
        self.cap = cv2.VideoCapture(camera_id)
        self.frame = None
        self.thresh = None
        self.is_touch = False
        self.is_hover = False
        self.cutoff_touch = 15
        self.cutoff_hover = 25
        self.aggl_clusterer = Agglomerative_Cluster_Model()
        # dominant fingertip memory
        self.last_fing_tip_coordinates:list = []
        # current dominant fingertip touch
        self.curr_dom_touch:list = []

    def cap_release(self):
        self.cap.release()

    def get_cutoff_touch(self):
        return self.cutoff_touch
    
    def get_cutoff_hover(self):
        return self.cutoff_hover

    def set_touch_cutoff(self, new_cutoff):
        self.cutoff_touch = new_cutoff

    def set_hover_cutoff(self, new_cutoff):
        self.cutoff_hover = new_cutoff

    def process_image(self):

        # Capture a frame from the webcam
        ret, frame = self.cap.read()

        # convert the frame to grayscale img for threshold filter and getting the contours of them
        img_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        ret_touch, thresh_touch = cv2.threshold(img_gray, self.cutoff_touch, 255, cv2.THRESH_BINARY)
        ret_hover, thresh_hover = cv2.threshold(img_gray, self.cutoff_hover, 255, cv2.THRESH_BINARY)
        
        contours_touch, hierarchy_touch = cv2.findContours(thresh_touch, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contours_hover, hierarchy_hover = cv2.findContours(thresh_hover, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        self.set_input_status(contours_touch, contours_hover)
        if self.is_touch:
            bounding_circle_radius = RADIUS_TOUCH
            bounding_circle_color = COLOR_TOUCH
            area_contours_clustered:list = self.get_clustered_points(contours_touch)
        else:
            bounding_circle_radius = RADIUS_HOVER
            bounding_circle_color = COLOR_HOVER
            area_contours_clustered:list = self.get_clustered_points(contours_hover)

        # convert back to colored img to see the touch areas
        img_bgr = cv2.cvtColor(img_gray, cv2.COLOR_BAYER_BG2BGR)

        final_areas:list = []
      
        for contour in area_contours_clustered:
            #area = cv2.contourArea(contour)
            
            (x,y),radius = cv2.minEnclosingCircle(contour)
            center = (int(x),int(y))
            radius = bounding_circle_radius
            cv2.circle(img_bgr,center,radius,bounding_circle_color,3)
            final_areas.append(contour)
    
        img_bgr = cv2.drawContours(img_bgr, final_areas, -1, (255, 160, 122), 3)

        return img_bgr
    
    def get_pyglet_image(self):
        img = None
        if self.frame is not None:
            img = cv2glet(self.frame, 'BGR')
        return img 
    
    def set_input_status(self, contours_touch:list, contours_hover:list):
        if len(contours_touch) > 1:
            self.is_touch = True
            self.is_hover = False
        else:
            if len(contours_hover) > 1:
                self.is_touch = False
                self.is_hover = True
            else:
                self.is_touch = False
                self.is_hover = False

    def get_clustered_points(self, contours:list):
        # contours of the touched areas
        touch_areas_contours:list = []

        for contour in contours:
            area = cv2.contourArea(contour)
            if area >= AREA_LOWER_LIMIT and area <= AREA_UPPER_LIMIT:
                touch_areas_contours.append(contour)
                
        area_contours_clustered = self.aggl_clusterer.agglomerative_clustering(touch_areas_contours)

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
                (x,y),radius = cv2.minEnclosingCircle(area_contours_clustered[i])
                if not self.last_fing_tip_coordinates:
                    self.last_fing_tip_coordinates.append((x,y))
                    self.last_fing_tip_coordinates.append((x,y))
                x_old, y_old = self.last_fing_tip_coordinates[i]
                if x_old - DEVIATION < x and x_old + DEVIATION > x and y_old - DEVIATION < y and y_old + DEVIATION > y:
                    area_contours_clustered[0] = self.curr_dom_touch[0]
                else:
                    self.last_fing_tip_coordinates[i] = (x,y)
                    self.curr_dom_touch[0] = area_contours_clustered[0]

        return area_contours_clustered