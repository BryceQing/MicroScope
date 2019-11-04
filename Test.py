import cv2
import numpy as np
img1 = cv2.imread('0x0.jpg')
img2 = cv2.imread('0x1.jpg')
img4 = cv2.imread('6x2.jpg')
img3 = np.vstack([img1, img2])
img3 = np.hstack([img3, img4])
cv2.imshow('Joint image', img3)
cv2.waitKey(0)