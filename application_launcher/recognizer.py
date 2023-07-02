# $1 gesture recognizer
#file is based on https://depts.washington.edu/acelab/proj/dollar/dollar.pdf
import math, os, csv
from typing import Type

class Point:
  def __init__(self, x: float, y: float) -> None:
    self.x = x
    self.y = y

class Config:
  SAMPLE_POINTS = 64
  SIZE = 250.0
  ORIGIN = Point(0,0)
  THETA_POS = 45.0
  THETA_NEG = -45.0
  THETA_DELTA = 2.0
  PHI = 0.5 * (-1.0 + math.sqrt(5.0))
  HALF_DIAGONAL = 0.5 * math.sqrt(SIZE * SIZE + SIZE * SIZE)
  REQUIRED_POINTS = 3

class Template:
  def __init__(self, index: int, name: str, points: list[Point]) -> None:
    self.index = index
    self.name = name
    self.points = points

def _distance(a: Point, b: Point) -> float:
  d_x = b.x - a.x
  d_y = b.y - a.y

  return math.sqrt(d_x * d_x + d_y * d_y)

def _resample(points: list[Point], n: int) -> list[Point]:
  I = _path_length(points) / (n - 1)
  D = 0.0

  new_points: list[Point] = []
  new_points.append(points[0])

  for (key, _) in enumerate(points):
    if key == 0:
      continue
    d = _distance(points[key - 1], points[key])

    if (D + d) >= I:
      q_x = points[key - 1].x + ((I - D) / d) * (points[key].x - points[key - 1].x)
      q_y = points[key - 1].y + ((I -D) / d) * (points[key].y - points[key - 1].y)
      
      new_point = Point(q_x, q_y)
      new_points.append(new_point)
      #need to insert the updated point into the initial list so that the next iteration can work with the updated point
      points.insert(key, new_point)

      D = 0.0

    else:
      D = D + d

  #https://depts.washington.edu/acelab/proj/dollar/dollar.js; addition to the pseudo code; sometimes the sample is one element too short
  if len(new_points) == n - 1:
    new_points.append(points[-1])
  
  return new_points

def _path_length(points: list[Point]) -> float:
  d = 0.0

  for i in range(1, len(points)):
    d = d + _distance(points[i - 1], points[i])

  return d

def _indicative_angle(points: list[Point]) -> float:
  c = _centroid(points)

  return math.atan2(c.y - points[0].y, c.x - points[0].x)


def _centroid(points: list[Point]) -> Point:
  l_x = [p.x for p in points]
  l_y = [p.y for p in points]

  return Point(sum(l_x) / len(points), sum(l_y) / len(points))

def _rotate_by(points: list[Point], theta: float) -> list[Point]:
  new_points: list[Point] = []
  c = _centroid(points=points) 
  sin = math.sin(theta)
  cos = math.cos(theta)

  for p in points:
    q_x = (p.x - c.x) * cos - (p.y - c.y) * sin + c.x
    q_y = (p.x - c.x) * sin + (p.y - c.y) * cos + c.y

    new_points.append(Point(q_x, q_y))
  
  return new_points

def _bounding_box(points: list[Point]) -> tuple[Point, Point]:
  l_x = [p.x for p in points]
  l_y = [p.y for p in points]

  min_x = min(l_x)
  max_x = max(l_x)
  min_y = min(l_y)
  max_y = max(l_y)
  
  return (Point(min_x, min_y), Point(max_x, max_y))

def _scale_to(points: list[Point], size: int) -> list[Point]:
  new_points: list[Point] = []
  b = _bounding_box(points=points)
  b_width = abs(b[1].x - b[0].x)
  b_height = abs(b[1].y - b[0].y)

  for p in points:
    q_x = p.x * (size / b_width)
    q_y = p.y * (size / b_height)

    new_points.append(Point(q_x, q_y))
  
  return new_points

def _translate_to(points: list[Point], origin: Point) -> list[Point]:
  new_points: list[Point] = []
  c = _centroid(points=points)

  for p in points:
    q_x = p.x + origin.x - c.x
    q_y = p.y + origin.y - c.y

    new_points.append(Point(q_x, q_y))

  return new_points

def _path_distance(points: list[Point], template: list[Point]) -> float:
  d = 0.0
  
  #https://stackoverflow.com/a/1663826/13620136
  for (p, t) in zip(points, template):
    d = d + _distance(p, t)

  return d / len(points)

def _distance_at_angle(points: list[Point], template: list[Point], theta: float) -> float:
  new_points = _rotate_by(points, theta)
  d = _path_distance(new_points, template)

  return d

def _distance_at_best_angle(points: list[Point], template: Template, phi: float, theta_neg: float, theta_pos: float, theta_delta: float) -> float:
  x_1 = phi * theta_neg + (1.0 - phi) * theta_pos
  f_1 = _distance_at_angle(points, template.points, x_1)

  x_2 = (1.0 - phi) * theta_neg + phi * theta_pos
  f_2 = _distance_at_angle(points, template.points, x_2)

  while abs(theta_pos - theta_neg) > theta_delta:
    if f_1 < f_2:
      theta_pos = x_2
      x_2 = x_1
      f_2 = f_1
      x_1 = phi * theta_neg + (1.0 - phi) * theta_pos
      f_1 = _distance_at_angle(points, template.points, x_1)

    else:
      theta_neg = x_1
      x_1 = x_2
      f_1 = f_2
      x_2 = (1.0 - phi) * theta_neg + phi * theta_pos
      f_2 = _distance_at_angle(points, template.points, x_2)

  return min(f_1, f_2)

def _convert_points(points: list[Point]) -> list[Point]:
    points = _resample(points, Config.SAMPLE_POINTS)
    rad = _indicative_angle(points)
    points = _rotate_by(points, -rad)
    points = _scale_to(points, Config.SIZE)
    points = _translate_to(points, Config.ORIGIN)

    return points

def _mirror_points(points: list[Point]) -> list[Point]:
  new_points = []
  for p in points:
    new_points.append(Point(-1 * p.x, p.y))

  return new_points

def _evaluate_list(points: list[Point]) -> bool:
  if len(points) <= Config.REQUIRED_POINTS:
    return False
  
  p_min, p_max = _bounding_box(points)

  if p_min.x == p_max.x or p_min.y == p_max.y:
    return False
  
  return True
      

class Recogniser:

  def __init__(self, ) -> None:
    self.templates: list[Template] = []

  def get_unique_template_names(self) -> list[str]:
    '''
      only returns unique template names because there is always a pair of a template because it is mirrored.
    '''
    template_names: list[str] = []

    for template in self.templates:
      template_names.append(template.name)

    return list(set(template_names))

  def load_templates(self, template_path: str, mappings: Type["Mapping"]=None) -> None:
    '''
      load templates from a path (folder) which contains multiple csv files. structure of these csv files is: idx,label,x,y,timestamp

    '''
    wanted_templates: list[str] = []
    for mapping in mappings:
      wanted_templates.append(mapping.gesture_name)

    if not os.path.exists(template_path):
      raise Exception("template path does not exist")

    for *_, files in os.walk(template_path):
      if len(files) == 0:
        continue

      for file_name in files:
        if not file_name.endswith(".csv"):
          continue

        file_path = os.path.join(template_path, file_name)

        with open(file_path, newline='') as csvfile:
          csv_reader = csv.reader(csvfile, delimiter=',')

          class_template = []
          class_name = None

          next(csv_reader)

          for row in csv_reader:
            class_name = row[1]
            class_template.append(Point(int(row[2]), int(row[3])))
          
          if class_name not in wanted_templates:
            continue
          else:
            wanted_templates.remove(class_name)

          self.add_template(class_name, class_template)
    
    if len(wanted_templates) != 0:
      raise Exception(f"some template names are not allowed: {', '.join(wanted_templates)}")

  def recognise(self, points: list[Point]) -> tuple[Template, float]:
    '''
      important note: length of list must be 2 or greater although it makes no sense to evaluate a path with 2 points. also the points must differentiate in x-axis and y-axis. e.g. point(10,10) and point(10,10) are not allowed because it results in a 0 length bounding box, throwing a division by zero error.
    '''
    if not _evaluate_list(points):
      return (None, None)

    points = _convert_points(points)

    b = float("infinity")
    found_template: Template = None

    for template in self.templates:
      d = _distance_at_best_angle(points, template, Config.PHI, Config.THETA_NEG, Config.THETA_POS, Config.THETA_DELTA)

      if d < b:
        b = d
        found_template = template

    score = 1.0 - (b / Config.HALF_DIAGONAL)
    
    return (found_template, score)

  def add_template(self, name: str, points: list[Point]) -> bool:
    '''
      adding _mirror_points which mirrors all points along the x-axis so that you avoid the 1$ recogniser limitation where only one draw direction for a gesture works
    '''
    if not _evaluate_list(points):
      return False

    converted_points = _convert_points(points)
    mirrored_points = _mirror_points(converted_points)
    
    template = Template(len(self.templates), name, converted_points)
    mirrored_template = Template(len(self.templates)+1, name, mirrored_points)

    self.templates.append(template)
    self.templates.append(mirrored_template)
    
    return True
