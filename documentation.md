# The "Osake-Touch"

![20230701_143320](https://github.com/ITT23/assignment-07-touch-device-osake/assets/41992838/313a7573-0ee2-4572-8c9f-902a70ad1f0e)

# Team Osake

## Michael Bierschneider

![20230701_094314](https://github.com/ITT23/assignment-07-touch-device-osake/assets/41992838/6e34f7dd-beec-4419-bd0a-afb924fbb080)

## Ruslan Asabidi

![20230701_094332](https://github.com/ITT23/assignment-07-touch-device-osake/assets/41992838/f1388381-d4fc-43ce-b6d4-86c8633ec072)

# Building of the Multitouch-Box (MT-Box)

### Building Process
- we assembled the bottom of the box, and taped it along the center and the edges to gain stability and avoid scattering light from the bottom
- we integrated a wooden board on the bottom of the box and taped the second bottom wings of the packages to the side so that the wodden board gets more stability and so that it does not distract the camera sensor
- the wooden board helps that the camera is always even (with card board there is always a bit of variance)
- we calculated (pi times thumb) the center of the bottom and taped the camera sensor with double-sided tape
- First we had integrated two connections for the camera into the box. One each for a USB type, because one of us didn't have a USB C port on the laptop. This circumstance was then remedied by buying an adapter and we left it with the USB C connection.
- we taped over the IR camera because it projected a lot of white dots onto the plexis glas which were reflected and resulted in distractions for the camera
  
- CHANGED CAMERA DEVICE: to Logitech camera, because the former camera made problems (to much integrated cameras)
  
#### Logitech Camera Device
![20230701_092840](https://github.com/ITT23/assignment-07-touch-device-osake/assets/41992838/ae6dfd00-5ccf-4842-a0fd-a1415d401b95)

- In order to further increase the stability of the camera, we fixed a block of wood in the middle of the wooden panel with screws and attached the camera to it with tape.


![20230701_092901](https://github.com/ITT23/assignment-07-touch-device-osake/assets/41992838/48ff88ee-b6a1-4a66-b3ac-16221bc4851a)

![20230701_093559](https://github.com/ITT23/assignment-07-touch-device-osake/assets/41992838/6912b71a-16d6-4913-8365-8722f1108843)

![20230701_094208](https://github.com/ITT23/assignment-07-touch-device-osake/assets/41992838/113a4ec3-0584-4df3-86ae-acfb27080182)

![WhatsApp Image 2023-07-01 at 10 40 20 (1)](https://github.com/ITT23/assignment-07-touch-device-osake/assets/41992838/090e44b0-72a6-4a8c-aac0-8b9989dee2f5)

![20230701_100000](https://github.com/ITT23/assignment-07-touch-device-osake/assets/41992838/80be5971-88fb-4475-bb1b-03633a971fdc)

- Since the camera shone a little on the side, we taped it off with adhesive tape on the side so that the unwanted light did not have to be taken into account for image processing.

![20230701_095502](https://github.com/ITT23/assignment-07-touch-device-osake/assets/41992838/6de333f0-e0c3-45d0-aa5b-86b2849ac725)

- In order to have access to the inside of the box at any time (e.g. to clean the glass plate from below), we installed the touch screen as a kind of lever.

![20230701_143332](https://github.com/ITT23/assignment-07-touch-device-osake/assets/41992838/b5f90cae-18f0-4fb5-9c23-ba3193133890)

- In the next step, we wanted to make the touch area recognizable for the user. To do this, we first clearly marked the touch area visually.

![20230701_103211](https://github.com/ITT23/assignment-07-touch-device-osake/assets/41992838/1d779bd7-b47d-43b3-b30e-e8b771de8831)

- However, we encountered a problem later on. The camera returned different images for two different device properties (in our case Windows and MacOs). With Windows, the touch area fitted exactly (was also drawn/determined on this basis). With the MacOs, however, the image was much larger and clearly encompassed large parts outside of the drawn touch area. Since several attempts to automatically adjust the image failed, we decided to work without a box drawn in. There was a risk that the size scaling was not only related to Windows and MacOs, but could also be affected by other device attributes, which posed the risk that even if we adjust it for Windows and MacOS, it would again be scaled incorrectly due to other causes could.

#### Osake-Touch with drawn Touch-Screen:

![20230701_104811](https://github.com/ITT23/assignment-07-touch-device-osake/assets/41992838/6f3ddbbf-e0dc-431e-83b5-aee18ab06aff)


#### Osake-Touch without drawn Touch-Screen (final result)

![20230701_143320](https://github.com/ITT23/assignment-07-touch-device-osake/assets/41992838/e599473f-c5a6-4cde-8fab-ad77d39b7894)

- Finally, we taped the box again at the most important points with adhesive tape to increase stability.


# Preparation and Prerequisits
- we needed to have a way to work on the assignment at home without carrieng the MT-Box with us. In order to be able to do that, we implemented a tool (webcam_recorder.py). It enables us to record webcam input and thus making some case samples (videos) to work with at home.
- in addtion to this tool we made a copy of the touch-input.py (main file for task 1) and called it touch-input_with_videos.py. It's used as a identical copy for touch-input.py but with the difference that is takes it video footage from pre-recorded vidos rather than real-time webcam input. In the further course, the functionality of the remote version "touch-input_with_videos.py" was integrated into "touch-input.py". As a result, if needed a video path is passed to the application when required. If not, the webcam is used.

# Detecting Touch and Hover
touch = strong touch

hover = light touch

cutoff = threshold value which decides whether a pixel of a gray image is detected. 

Example: 0 = pixel would need to be complete black, 255 = complete white

## coresponding files
- touch-input.py  -> main file
- helper/webcam_recorder.py -> recording video for remote sessions
- touch_sensor/AppState.py -> Enums for different application states like the calibration stapes
- touch_sensor/calibration.txt -> contains cutoff values for touch and hover (overwritten/used after the calibration process)
- touch_sensor/Clustering.py -> agglomerative clustering of detected contours
- touch_sensor/Config.py -> stores magic numbers, strings and the dippid attribute ID
- touch_sensor/Helper.py -> contains class for the capture, image processing and Dippid functionality
- assets -> contained our recorded videos (now deleted)

## Procedure
- we differentiate toch and hover based on cutoff.
- first the frame gets converted to a gray image
- we apply the dilate and erode filters to better distinguish the touched/hovered areas
- in the next step the filtered gray image gets its contoures detected twice. First with the cutoff value for touch and then for the cutoff value for hover.
- based on the resulting contours the input gets interpreted as touch, hover or none of both (areas are analysed).
- in the next step we used a agglomerative clustering algorithm to cluster the resulting contours to touch/hover points. 
- touch and hover input is shown as boundig 'box' circles
- to distinguish both the touch bbox circle is bigger and has a different color than the hover one.
- while the detection worked we encountered the problem that the resulting bbox circle vibrated. The reason was that even if you hold still your fingertip the input x and y point changes slightly which causes this vibration. To prefend it we saved for every input its last input coordinates and compared the new one with it (example: last x_coordinate - deviation <= new x_coordinate <= last x_coordinate + deviation). In addition to that, it is checked if the last 5 inputs where touch, hover or none of both and based on the trend it decides if a new input accuring to be none most certainly again is a touch or hover or indeed none of both. All this steps helps to minimazie the pulsation of the bbox circle and further more prevents a "touch/hover release event" happening in task 2 and 3 when indeed the user did'nt release (even if the estimated cutoffs for hover and touch after the calibration is quite accurate it can happen that a input isn't reliable recogniced as touch or hover; this steps helps us to takle this problem).

## Calibration

The calibration uses the image processing method as described in the Procedure section. However, the cutoff start value of 20 is used for touch and hover. The following logic is then used to determine the cutoff value for each touch and hover:

- First of all, users are informed (all information on the screen is scaled to the image size) that they should place their finger on the touch display. For touch with the fingertip and for hover with the fingernail. Once the user is ready, the user presses the "c" key and the corresponding calibration begins. To do this, users should draw around on the display without lifting their finger (the event that they do so or get out of the camera's viewing angle is taken into account). If nothing is detected, the corresponding cutoff of the touch or hover calibration to be checked is increased by 1.

- If more than the finger input is detected, the corresponding cutoff is reduced by 1.

- If the user lifts their finger or leaves the camera area, the cutoff value quickly explodes above 90. In this case, the cutoff is reset to its original value of 20 and the calibration continues again and the value is further adjusted.

- Whether the calibration for touch/hover was successful is checked by saving successes and failures. After a certain number of analyzed images, it is checked whether 90 percent of them for touch/hover (depending on which of the two is calibrated) were successful.

- The steps in normal image processing to reduce the vibration of the circled bbox are not used in calibration.

- The calibrated values ​​are also saved in calibration.txt if you want to skip calibration next time. These are then automatically taken accordingly.

- The calibration process can be repeated at any time by pressing the "c" key.

- window is closed after calibration (processing and sending of events happens in the background)

### Examples

#### Hover Calibration

![cali_hover](https://github.com/ITT23/assignment-07-touch-device-osake/assets/41992838/4e44c3b3-3ebb-4ed4-956a-7aa4adde2342)

#### Touch Calibration

![cali_touch](https://github.com/ITT23/assignment-07-touch-device-osake/assets/41992838/30cf546b-2c19-43fd-8a8f-06a2ae211d03)

#### After Calibration (2-Finger-Touch)

![cali_double](https://github.com/ITT23/assignment-07-touch-device-osake/assets/41992838/b460785c-36ed-4dc1-babf-db5a40b0611d)

# Usage

## DIPPID:
- 5700 is used as port
- "127.0.0.1" is used as ID (adjust in Config.py if necessary)

## Start application:
adjust --video_id if necessary

### in DEBUG mode:
py touch-input.py --video_id 1 -s debug

### start with calibration:
py touch-input.py --video_id 1 -s calibration

### start without calibration (use values from last calibration):
py touch-input.py --video_id 1 -s default ("default" can also be omitted)

## Key Events
q -> closes/exits touch-input application
c -> while calibration: inits calibration steps; after calibration: restarts calibration

# Sources:

agglomerative clustering
https://cullensun.medium.com/agglomerative-clustering-for-opencv-contours-cd74719b678e

convert cv2 image to pyglet image
https://gist.github.com/nkymut/1cb40ea6ae4de0cf9ded7332f1ca0d55

scale font size of text to the image size
https://www.appsloveworld.com/opencv/100/3/how-to-resize-text-for-cv2-puttext-according-to-the-image-size-in-opencv-python





