# Getting Started with Images
# Using OpenCV
# Courtney Banh, Nick Vaughn

import numpy as np
import cv2

####### Read an image #######

# Load a color image in grayscale
img = cv2.imread('/home/pi/Desktop/Basha.jpg',0)
##print(img)

####### Display an image #######

##cv2.imshow('Dr. Basha', img)
##cv2.waitKey(0)
##cv2.destroyAllWindows()

cv2.namedWindow('Resizable Basha', cv2.WINDOW_NORMAL)
cv2.imshow('Resizable Basha',img)
cv2.waitKey(0)
cv2.destroyAllWindows()

####### Write an image #######

cv2.imwrite('BashaGray.png',img)

