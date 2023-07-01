# Agglomerative Clustering of the detected contours
# https://cullensun.medium.com/agglomerative-clustering-for-opencv-contours-cd74719b678e

import cv2
import numpy as np

from Config import Config

class Clustering:

  def cluster(self, contours: list, threshold_distance=Config.CLUSTERING_THRESHOLD):
    while len(contours) > 1: 
      min_distance = None
      min_coordinate = None

      for x in range(len(contours)-1):
        for y in range(x+1, len(contours)):
          distance = calculate_contour_distance(contours[x], contours[y])
          
          if min_distance is None:
            min_distance = distance
            min_coordinate = (x, y)

          elif distance < min_distance:
            min_distance = distance
            min_coordinate = (x, y)

      if min_distance < threshold_distance:
        index1, index2 = min_coordinate
        contours[index1] = np.concatenate((contours[index1], contours[index2]), axis=0)
        
        del contours[index2]
      
      else:
        break

    return contours
        
def calculate_contour_distance(contour1, contour2): 
  x1, y1, w1, h1 = cv2.boundingRect(contour1)
  c_x1 = x1 + w1/2
  c_y1 = y1 + h1/2

  x2, y2, w2, h2 = cv2.boundingRect(contour2)
  c_x2 = x2 + w2/2
  c_y2 = y2 + h2/2

  return max(abs(c_x1 - c_x2) - (w1 + w2)/2, abs(c_y1 - c_y2) - (h1 + h2)/2)