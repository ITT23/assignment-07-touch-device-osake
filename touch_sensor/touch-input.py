import time, os, keyboard, cv2

from argparse import ArgumentParser, ArgumentTypeError

from Helper import Image_Processor, DIPPID_Sender, Capture, Calibration
from AppState import AppState, CalibrationState


class Application:

  CURR_DIR = os.path.dirname(__file__)
  CALIBRATION_FILE = os.path.join(CURR_DIR, "calibration.txt")

  def __init__(self, video_path: str, video_id: int, dippid_port: int, state: AppState, eps: int) -> None:
    self.video_path = video_path
    self.video_id = video_id
    self.dippid_port = dippid_port
    self.state = state
    self.eps = 1 / eps
    self.capture = Capture(self.video_path, self.video_id)
    self._video_dimensions = (self.capture.width, self.capture.height)
    self.image_processor = Image_Processor(video_dimensions=self._video_dimensions)
    self.calibration_proc = Calibration(self.capture, self.image_processor)
    
    self.calibration = {
      "CUTOFF_TOUCH": 0,
      "CUTOFF_HOVER": 0,
    }

    # load calibration values
    ## init calibration process to calculate the values
    if self.state == AppState.CALIBRATION:
      self._perform_calibration()
    ## scip calibration and load values from the last calibration process
    else:
      self._load_calibration_values()

    # use-case: useage of prerecorder videos
    if self.video_path is not None:
      path = os.path.join(self.CURR_DIR, self.video_path)
      if not os.path.exists(path):
        raise Exception("provided path to videos does not exist")

    self.sender = DIPPID_Sender(self.dippid_port)   
    self.running = True

  def _perform_calibration(self) -> None:
    self.calibration_proc.set_status()
  
  def _load_calibration_values(self) -> None:
    with open(self.CALIBRATION_FILE, "r") as f:
      content = f.read().split("\n")
      
      for line in content:
        name, value = line.split(" ")

        self.calibration[name] = value
    self.image_processor.apply_calibration_cutoff(self.calibration)

  def run(self) -> None:
    while self.running:
      # check if touch or hover happened
      ret, frame = self.capture.next_image()

      if not ret:
        print("no frames to process... terminating application")
        break
      
      # get processing time for the image processing of a frame (de-comment corresponding lines below if needed)
      #t1 = time.time()
      success, processed_img, output = self.image_processor.process_image(frame)
      #t2 = time.time()
      if self.state == AppState.DEBUG:
        pass
        #print(f"processing time for this frame was {t2-t1} seconds.")

      # add calibration info to the image (if calibration active)
      if self.calibration_proc.active == True:
        processed_img = self.calibration_proc.set_info_txt(processed_img)
        self.calibration_proc.calibrate_cutoff()

      # if calibration finished (or skiped -> close window)
      if self.calibration_proc.active == False:
        cv2.destroyAllWindows()

      # show window just in the calibration process
      if (self.state is not AppState.DEFAULT and self.calibration_proc.active == True) or self.state is AppState.DEBUG:
        self.capture.show_frame(processed_img)

      # send dippid data (not while the calibration process)
      if success == True and self.calibration_proc.active == False:
        self.sender.send_event(output, self.state)

      # key events
      ## do the calibration process again (in case the user wants to re-calibrate)
      if keyboard.is_pressed('c') and self.calibration_proc.active == False:
        self.calibration_proc.set_status()
      # quit while the calibration process is not active
      if keyboard.is_pressed('q') and self.calibration_proc.active == False:
        self.running = False
        self.capture.release()
        cv2.destroyAllWindows()
        
      # quit while the calibration process is active
      if cv2.waitKey(1) & 0xff == ord('q'):
        self.running = False
        self.capture.release()
        cv2.destroyAllWindows()
      # init next step of the calibration process

      if cv2.waitKey(1) & 0xff == ord('c') and self.calibration_proc.active == True:
        if self.calibration_proc.state == CalibrationState.HOVER_INFO:
          self.calibration_proc.state = CalibrationState.HOVER
          self.image_processor.state = CalibrationState.HOVER
        if self.calibration_proc.state == CalibrationState.TOUCH_INFO:
          self.calibration_proc.state = CalibrationState.TOUCH
          self.image_processor.state = CalibrationState.TOUCH

      if self.eps > 0:
        time.sleep(self.eps)


def check_eps_value(value: int) -> str:
  if value == 0 or value < -1 or value > 120:
    raise ArgumentTypeError(f"eps value can not be 0. allowed values: [-1, 1...120]")
  
  return value


if __name__ == "__main__":
  parser = ArgumentParser(prog="AR Game", description="crazy ar game.")
  
  group = parser.add_mutually_exclusive_group()
  group.add_argument("--video_path", default=None, type=str, help="relative path to video record")
  group.add_argument("--video_id", default=0, type=int, help="id of webcam found in evtest")
  
  parser.add_argument("-p", default=5700, type=int, help="dippid port")
  parser.add_argument("-s", default="default", type=str, choices=[state.name.lower() for state in AppState], \
                      help="enable debug mode: print DIPPID formated data to terminal instead of sending it to dgram server; \
                        enable calibration mode: terminates the cutoff values for hover and touch events which are saved to file; \
                          default: start sending touch events to dgram server")
  parser.add_argument("-e", default=-1, type=int, help="determine maximal events per seconds. provide an integer like 4 -> 1/4 events per second. \
                      per default runs with maximum eps (eps==-1).")

  args = parser.parse_args()

  application = Application(video_path= args.video_path, video_id=args.video_id, dippid_port=args.p, state=AppState[args.s.upper()], eps=args.e)

  application.run()

   # py touch-input.py --video_id 1 -s debug
   # py touch-input.py --video_id 0 -s calibration