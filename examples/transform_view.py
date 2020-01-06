import cv2
import numpy as np
# load CARLA example image 
image = cv2.imread('00004746.png')
# define four corners in original image
src = np.float32([[200, 720], [1100, 720], [500, 450], [700, 450]])
# define where the corners end up after transformation
dst = np.float32([[300, 720], [900, 720], [300, 0], [900, 0]])

img_size = (image.shape[1],image.shape[0])
# Compute perspective tranform from sorce and destination
M = cv2.getPerspectiveTransform(src, dst)
# Use transform to warp source image
warped = cv2.warpPerspective(image, M, img_size)

cv2.imshow('image',warped)
cv2.waitKey(0)  
cv2.destroyAllWindows()