import cv2
import pyglet

from PIL import Image
from pyglet import shapes

from collections import deque

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
        self.dom_fing_coordinates:list = deque(maxlen=1)
        # current dominant fingertip touch
        self.curr_dom_touch:list = deque(maxlen=1)

    def cap_release(self):
        self.cap.release()

    def set_touch_state(self, touch_variant:str, state:bool):
        if touch_variant == 'touch':
            self.is_touch = state
        elif touch_variant == 'hover':
            self.is_hover = state
    
    def get_touch_state(self):
        return self.is_touch
    
    def get_hover_state(self):
        return self.is_hover

    def get_cutoff_touch(self):
        return self.cutoff_touch
    
    def get_cutoff_hover(self):
        return self.cutoff_hover

    def set_touch_cutoff(self, new_cutoff):
        self.cutoff_touch = new_cutoff

    def set_hover_cutoff(self, new_cutoff):
        self.cutoff_hover = new_cutoff

    def process_image(self, touch_variant:str): # touch_variant is "touch" or "hover"
        #cutoff = 0
        #bounding_circle_radius = 0
        #bounding_circle_color = None
        
        if touch_variant == 'touch':
            cutoff = self.cutoff_touch
            bounding_circle_radius = RADIUS_TOUCH
            bounding_circle_color = COLOR_TOUCH
        elif touch_variant == 'hover':
            cutoff = self.cutoff_hover
            bounding_circle_radius = RADIUS_HOVER
            bounding_circle_color = COLOR_HOVER
        else:
            raise Exception("use 'touch' or 'hover'")

        # Capture a frame from the webcam
        ret, frame = self.cap.read()

        # convert the frame to grayscale img for threshold filter and getting the contours of them
        img_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        ret, thresh = cv2.threshold(img_gray, cutoff, 255, cv2.THRESH_BINARY)
        
        contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        # convert back to colored img to see the touch areas
        img_bgr = cv2.cvtColor(img_gray, cv2.COLOR_BAYER_BG2BGR)

        # contours of the touched areas
        touch_areas_contours:list = []

        for contour in contours:
            area = cv2.contourArea(contour)
            if area >= AREA_LOWER_LIMIT and area <= AREA_UPPER_LIMIT:
                #(x,y),radius = cv2.minEnclosingCircle(contour)
                #center = (int(x),int(y))
                #radius = int(radius) * 3
                #cv2.circle(img_gray,center,radius,(0,255,0),3)q
                touch_areas_contours.append(contour)
                
        area_contours_clustered = self.aggl_clusterer.agglomerative_clustering(touch_areas_contours)
            
        final_areas:list = []
        
        # Flackern reduzieren
        # old or new position
        # öö
        if len(area_contours_clustered) > 0:
            self.set_touch_state(touch_variant, True)
            (x,y),radius = cv2.minEnclosingCircle(area_contours_clustered[0])
            print((x,y))
            if len(self.dom_fing_coordinates) == 0:
                self.dom_fing_coordinates.append((x,y))
            if len(self.curr_dom_touch) == 0:
                self.curr_dom_touch.append(area_contours_clustered[0])
            x_old, y_old = self.dom_fing_coordinates[0]
            if x_old - DEVIATION < x and x_old + DEVIATION > x and y_old - DEVIATION < y and y_old + DEVIATION > y:
                area_contours_clustered[0] = self.curr_dom_touch[0]
            else:
                self.dom_fing_coordinates.append((x,y))
                self.curr_dom_touch.append(area_contours_clustered[0])
        else:
            self.set_touch_state(touch_variant, False)
            
        for contour in area_contours_clustered:
            area = cv2.contourArea(contour)
            
            (x,y),radius = cv2.minEnclosingCircle(contour)
            center = (int(x),int(y))
            radius = bounding_circle_radius
            cv2.circle(img_bgr,center,radius,bounding_circle_color,3)
            final_areas.append(contour)
    
        img_processed = cv2.drawContours(img_bgr, final_areas, -1, (255, 160, 122), 3)

        return img_processed
    
    def get_pyglet_image(self):
        img = None
        if self.frame is not None:
            img = cv2glet(self.frame, 'BGR')
        return img 
    

    '''
    def get_raw_image(self):
        ret, frame = self.cap.read()
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # transform to grayscale, apply threshold
        # this allows for pixel-perfect collision detection
        # another method could be to find the contours and detect collision with the resulting polygon
        gray_transformed = cv2.cvtColor(frame_transformed, cv2.COLOR_BGR2GRAY)
        ret, thresh = cv2.threshold(gray_transformed, 160, 255, cv2.THRESH_BINARY_INV)

        self.thresh = thresh
        out = frame_transformed

        self.frame = out
'''