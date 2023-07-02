from typing import Type
import math

class Vector:

  def __init__(self, x: int, y: int) -> None:
    self.x = x
    self.y = y

  def calc_angle(self, new_vector: Type["Vector"]) -> float:
    dot_product = self.x * new_vector[0] + self.y * new_vector[1]
    norm_vector1 = math.sqrt(self.x ** 2 + self.y ** 2)
    norm_vector2 = math.sqrt(new_vector[0] ** 2 + new_vector[1] ** 2)
    cos_theta = dot_product / (norm_vector1 * norm_vector2)
    theta = math.acos(cos_theta)
    angle_degrees = math.degrees(theta)

    return angle_degrees

  def calc_distance(self, new_vector: Type["Vector"]) -> float:
    dx = (self.x - new_vector[0])
    dy = (self.y - new_vector[1])
    distance_fingers = math.sqrt(dx ** 2 + dy ** 2)

    return distance_fingers