from picamera import PiCamera
from time import sleep

camera = PiCamera()

camera.start_preview()
camera.start_recording('/home/pi/Desktop/Basha_vid.h264')
sleep(10)
#camera.capture('/home/pi/Desktop/Basha.jpg')
camera.stop_recording()
camera.stop_preview()