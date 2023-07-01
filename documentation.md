# Documentation

# Team

## Michael Bierschneider
![20230701_094314](https://github.com/ITT23/assignment-07-touch-device-osake/assets/41992838/6e34f7dd-beec-4419-bd0a-afb924fbb080)

## Ruslan Asabidi
![20230701_094332](https://github.com/ITT23/assignment-07-touch-device-osake/assets/41992838/f1388381-d4fc-43ce-b6d4-86c8633ec072)

## Building of the Multitouch-Box (MT-Box)

- we assembled the bottom of the box, and taped it along the center and the edges to gain stability and avoid scattering light from the bottom
- we integrated a wooden board on the bottom of the box and taped the second bottom wings of the packages to the side so that the wodden board gets more stability and so that it does not distract the camera sensor
- the wooden board helps that the camera is always even (with card board there is always a bit of variance)
- we calculated (pi times thumb) the center of the bottom and taped the camera sensor with double-sided tape
- we taped over the IR camera because it projected a lot of white dots onto the plexis glas which were reflected and resulted in distractions for the camera
- CHANGED CAMERA DEVICE: to Logitech camera, because the former camera made problems (to much integrated cameras)

## Preparation and Prerequisits
- we needed to have a way to work on the assignment at home without carrieng the MT-Box with us. In order to be able to do that, we implemented a tool (webcam_recorder.py). It enables us to record webcam input and thus making some case samples (videos) to work with at home.
- in addtion to this tool we made a copy of the touch-input.py (main file for task 1) and called it touch-input_with_videos.py. It's used as a identical copy for touch-input.py but with the difference that is takes it video footage from pre-recorded vidos rather than real-time webcam input. 

## Detecting Touch and Hover
touch = strong touch
hover = light touch
cutoff = threshold value which decides whether a pixel of a gray image is detected. 
Example: 0 = pixel would need to be complete black, 255 = complete white

### coresponding files
- touch-input.py / touch-input_with_videos.py  -> main file
- agglomerative_clustering_class.py -> class used to cluster detected contours of an image with the agglomerative clustering algorithm
source: https://cullensun.medium.com/agglomerative-clustering-for-opencv-contours-cd74719b678e
- touch_input_classes.py -> contains the Image_Processor class to process an image in regard to touch and hover and the DIPPID_Sender class to send the events via dippid

### Procedure
- we differentiate toch and hover based on cutoff.
- first the frame gets converted to a gray image
- for the following steps we need the cutoff value for touch and hover, which are determined in the calibration process 
(calibration process yet not implemented. For now we use predefined cutoff values. [26.06.23])
- in the next step the gray image gets its contoures detected twice. First with the cutoff value for touch and then for the cutoff value for hover.
- based on the resulting contours the input gets interpreted as touch, hover or none of both.
- in the next step we used a agglomerative clustering algorithm to cluster the resulting contours to touch/hover points. 
- touch and hover input is shown as boundig 'box' circles
- to distinguish both the touch bbox circle is bigger and has a different color than the hover one.
- while the detection worked we encountered the problem that the resulting bbox circle vibrated. The reason was that even if you hold still your fingertip the input x and y point changes slightly which causes this vibration. To prefend it we saved for every input its last input coordinates and compared the new one with it (example: last x_coordinate - deviation <= new x_coordinate <= last x_coordinate + deviation)

