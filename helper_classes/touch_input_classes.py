import cv2

# own helper classes
from helper_classes.agglomerative_clustering_class import Agglomerative_Cluster_Model

class ImageHandler:
    def __init__(self, camera_id):
        self.cap = cv2.VideoCapture(camera_id)
        self.frame = None
        self.thresh = None
        self.radius_touch = 40
        self.radus_hover = 60
        self.is_touch = False
        self.is_hover = False
        self.cutoff_touch = 0
        self.cutoff_hover = 0
        self.area_lower_limit = 0
        self.area_upper_limit = 50
        self.deviation = 50
        self.aggl_clusterer = Agglomerative_Cluster_Model()
        # dominant fingertip memory
        self.dom_fing_coordinates:tuple = None
        # current dominant fingertip touch
        self.curr_dom_touch = None

    def get_cutoff_touch(self):
        return self.cutoff_touch
    
    def get_cutoff_hover(self):
        return self.cutoff_hover

    def set_touch_cutoff(self, new_cutoff):
        self.cutoff_touch = new_cutoff

    def set_hover_cutoff(self, new_cutoff):
        self.cutoff_hover = new_cutoff

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

    def get_pyglet_image(self, touch_variant:str): # touch_variant is "touch" or "hover"
        cutoff = 0
        bounding_cirle_radius = 0
        
        if touch_variant == 'touch':
            cutoff = self.cutoff_touch
            bounding_cirle_radius = self.radius_touch
        elif touch_variant == 'hover':
            cutoff = self.cutoff_hover
            bounding_cirle_radius = self.radus_hover
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
            if area >= self.area_lower_limit and area <= self.area_upper_limit:
                #(x,y),radius = cv2.minEnclosingCircle(contour)
                #center = (int(x),int(y))
                #radius = int(radius) * 3
                #cv2.circle(img_gray,center,radius,(0,255,0),3)q
                touch_areas_contours.append(contour)
                
        area_contours_clustered = self.aggl_clusterer.agglomerative_clustering(touch_areas_contours)
            
        final_areas:list = []
        
        # Flackern reduzieren
        # old or new position
        if len(area_contours_clustered) > 0:
            (x,y),radius = cv2.minEnclosingCircle(area_contours_clustered[0])
            if self.dom_fing_coordinates == None:
                self.dom_fing_coordinates = (x,y)
            if self.curr_dom_touch == None:
                self.curr_dom_touch = area_contours_clustered[0]
            x_old, y_old = self.dom_fing_coordinates
            if x_old - self.deviation < x and x_old + self.deviation> x and y_old - self.deviation < y and y_old + self.deviation > y:
                area_contours_clustered[0] = self.curr_dom_touch
            else:
                self.dom_fing_coordinates = (x,y)
                self.curr_dom_touch = area_contours_clustered[0]
                
        for contour in area_contours_clustered:
            area = cv2.contourArea(contour)
            
            (x,y),radius = cv2.minEnclosingCircle(contour)
            center = (int(x),int(y))
            radius = bounding_cirle_radius
            cv2.circle(img_bgr,center,radius,(0,255,0),3)
            final_areas.append(contour)
    
        img_processed = cv2.drawContours(img_bgr, final_areas, -1, (255, 160, 122), 3)

        return img_processed



        img = None
        if self.frame is not None:
            img = cv2glet(self.frame, 'BGR')
        return img 