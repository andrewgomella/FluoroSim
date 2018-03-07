# FluoroSim
an interventional radiology geared fluoroscopy simulator using a raspberry pi3 with webcam
As presented at the Society of Interventional Radiology 2018 meeting in Los Angeles. 
https://www.sirmeeting.org/

## Parts
Raspberry Pi 3
Microsd card
Webcam (we use Logitech C270, although any vl42 compatible webcam will work)
USB light (or any lighting to adequately illuminate the phantom) 
Foot pedal (any momentary foot switch can be used, alternatively the space-bar on a keyboard can be used)
Phantom (created from trasnparent polyethylene tubing and Loctite plastics binding system)
Hdmi monitor 

## Raspberry Pi Setup
Install raspbian on the microsd card to be placed in the raspberry. 
Detailed instructions can be found here: https://www.raspberrypi.org/documentation/installation/installing-images/
Install OpenCV along with python bindings
Install the RPi.GPIO library https://pypi.python.org/pypi/RPi.GPIO for use of the foot pedal
Download fluoro-simulator.py and run with "python fluoro-simulator.py" from the terminal
The foot pedal was wired into the GPIO4 (Pin #07) and DC Power 3.3V (Pin #01) on the Raspberry Pi. If needed you may change these in the fluoro-simulator.py file to reflect your requirements. 

## Overlay
Choose an overlay image that is appropriate for your transparent phantom. Place the overlay image into the same directory as fluorosim.py and name it according the OVERLAY_IMAGE variable, which comes preset as skel.jpg. Four our demo we use an abdominal radiograph from wikipedia found here: https://en.wikipedia.org/wiki/Abdominal_x-ray
https://en.wikipedia.org/wiki/Abdominal_x-ray#/media/File:Medical_X-Ray_imaging_ALP02_nevit.jpg

## Operation
Usage(in the terminal)
   fluoro_sim.py {<video device number>}

Keyboard shortcuts:
   ESC - exit
   Space - Toggle Peddle
   1 - Toggle Overlay
   2 - Toggle Subtraction
   3 - Fullscreen
   4 - Windowed mode
   5 - Retake background image used in subtraction
   6 - Equalize histogram




