'''
TODO:
- nahebeieinanderliegende areas gruppieren 
- Kalibrierung ausprobieren
  -> Cutoff nachjustieren bis Wert erziehlt wird 
  -> Zu Beginn soll der Kalibrierungsprozess stattfinden (user soll darüber informiert werden)
            -> für cutoff und Lichtverhältnisse
            -> Zwischen light und strong Touch (eventuell über die Größe der Area)
- Flickern reduzieren (letzte Zustände speichern)

HERE CALIBRATION PROCESS
über pyglet

nutzer sollen hovern solange bis was erkannt wird und vor allem flüssig hintereinander
-> sobald nicht erkannt wird soll cutoff +1 erhöht werden (von touch oder hover; je nachdem was grad kalibriert wird)
das Gleiche für touch
eventuell timer einbauen bevor kalibrierung beginnt, damit Nutzer Zeit haben den finger zu positionieren 
(da sonst cutoff explodiert)

sobald Kalibrierung beendet wird, soll pyglet schließen und der untere while Code tritt in Kraft (Anzeige des frames raus; dippid sender code das auskommentierte wieder rein)
'''
import time, os
import pyglet
from argparse import ArgumentParser, ArgumentTypeError

import cv2

from os import path

from Helper import Image_Processor, DIPPID_Sender, Capture, Calibration
from AppState import AppState

#CURR_DIR = path.dirname(__file__)
#RECORDED_SESSION = path.join(CURR_DIR, "../assets/gestures/check_hover_1.mp4")

class Application:

  CURR_DIR = os.path.dirname(__file__)
  CALIBRATION_FILE = os.path.join(CURR_DIR, "calibration.txt")

  def __init__(self, video_path: str, video_id: int, dippid_port: int, state: AppState, eps: int) -> None:
    self.video_path = video_path
    self.video_id = video_id
    self.dippid_port = dippid_port
    self.state = state
    self.eps = 1 / eps

    self.calibration = {
      "CUTOFF_TOUCH": 0,
      "CUTOFF_HOVER": 0,
    }

    ### load calibration values
    if self.state == AppState.CALIBRATION:
      self._perform_calibration()
      #TODO: exit app after calibrating

    else:
      self._load_calibration_values()

    if self.video_path is not None:
      path = os.path.join(self.CURR_DIR, self.video_path)
      if not os.path.exists(path):
        raise Exception("provided path to videos does not exist")

    self.capture = Capture(self.video_path, self.video_id)
    self._video_dimensions = (self.capture.width, self.capture.height)
    self.image_processor = Image_Processor(video_dimensions=self._video_dimensions, calibration=self.calibration)
    self.sender = DIPPID_Sender(self.dippid_port)   

    self.running = True

  def _perform_calibration(self) -> None:
    #print("NYI")#TODO
    #pass
    window = pyglet.window.Window(self.capture.width, self.capture.height, resizable=False)
    batch = pyglet.graphics.Batch()
    
    calibration = None

    @window.event
    def on_draw():
        if calibration is not None:
            window.clear()
            calibration.draw()
            batch.draw()

    if __name__ == "__main__":
        calibration = Calibration()
        pyglet.clock.schedule_interval(calibration.update, 0.2)
        pyglet.app.run()
    

  def _load_calibration_values(self) -> None:
    with open(self.CALIBRATION_FILE, "r") as f:
      content = f.read().split("\n")
      
      for line in content:
        name, value = line.split(" ")

        self.calibration[name] = value

  def run(self) -> None:
    while self.running:
      # check if touch or hover happened
      ret, frame = self.capture.next_image()

      if not ret:
        #print("no frames to process... terminating application")
        break

      t1 = time.time()
      success, processed_img, output = self.image_processor.process_image(frame)
      t2 = time.time()
      if self.state == AppState.DEBUG:
        pass
        #print(f"processing time for this frame was {t2-t1} seconds.")
      
      if self.state is not AppState.DEFAULT:
        self.capture.show_frame(processed_img)
      
      if success:
        self.sender.send_event(output, self.state)

      # Wait for a key press and check if it's the 'q' key
      # just for testing purposes, but later it could init a new calibration process
      if cv2.waitKey(1) & 0xff == ord('q'):
        self.running = False
        self.capture.release()
        cv2.destroyAllWindows()

      if self.eps > 0:
        time.sleep(self.eps)


def check_eps_value(value: int) -> str:
  if value == 0 or value < -1 or value > 120:
    raise ArgumentTypeError(f"eps value can not be 0. allowed values: [-1, 1...120]")
  
  return value


if __name__ == "__main__":
  parser = ArgumentParser(prog="AR Game", description="crazy ar game.")
  
  group = parser.add_mutually_exclusive_group()
  group.add_argument("--video_path", default="../assets/gestures/check_hover_2.mp4", type=str, help="relative path to video record")
  group.add_argument("--video_id", default=0, type=int, help="id of webcam found in evtest")
  
  parser.add_argument("-p", default=5700, type=int, help="dippid port")
  parser.add_argument("-s", default="default", type=str, choices=[state.name.lower() for state in AppState], help="enable debug mode: print DIPPID formated data to terminal instead of sending it to dgram server; enable calibration mode: terminates the cutoff values for hover and touch events which are saved to file; default: start sending touch events to dgram server")
  parser.add_argument("-e", default=-1, type=int, help="determine maximal events per seconds. provide an integer like 4 -> 1/4 events per second. per default runs with maximum eps (eps==-1).")

  args = parser.parse_args()

  application = Application(video_path= args.video_path, video_id=args.video_id, dippid_port=args.p, state=AppState[args.s.upper()], eps=args.e)

  application.run()

   # py touch-input.py --video_id 1 -s debug