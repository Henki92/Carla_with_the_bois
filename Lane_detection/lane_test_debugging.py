import cv2
import numpy as np
import matplotlib.pyplot as plt

IMAGE_HEIGHT = 769
IMAGE_WIDTH = 1279
HSV_B = 10
HSV_G = 160
HSV_R = 255
HSV_EXP = 26
HSV_THRESHOLD = 85
RGB_B = 60
RGB_G = 110
RGB_R = 90
RGB_EXP = 12
RGB_THRESHOLD = 125
window_processed_image = "Processed image"
ROI_BOTTOM = 722
ROI_TOP = round(722/3)
ROI_LEFT = 0
ROI_RIGHT = 1279

# Get image from carla but for now just take a png file
original_img = cv2.imread('example.jpg', cv2.IMREAD_ANYCOLOR)
# Display image
cv2.imshow('Original image', original_img)

# Define ROI and remove everything else
roi_image = original_img.copy()
roi_image[0:ROI_TOP, ROI_LEFT:ROI_RIGHT] = 0

# Convert orignal to grayscale and set threshold
# We want yellow and white to be brighter, this is the lane colors in carla
# OPENCV does BGR format
w = np.array([[[RGB_B / 255, RGB_G / 255, RGB_R / 255]]])
gray_img2 = cv2.convertScaleAbs(np.sum(roi_image * w, axis=2))

# Darken grayscale image
dark_gray_img2 = np.power(gray_img2.astype('uint16'), RGB_EXP / 10)
max_value = np.max(dark_gray_img2)


dark_gray_img2 = np.round(np.multiply(np.divide(dark_gray_img2, max_value), 255)).astype('uint8')
filtered_image_RGB = cv2.inRange(dark_gray_img2, RGB_THRESHOLD, 255)
cv2.imshow("RGB processed", filtered_image_RGB)

# Convert orignal to HSV colorspace and then grayscale and set threshold
# We want yellow and white to be brighter, this is the lane colors in carla
# OPENCV does BGR format
frame = cv2.cvtColor(roi_image, cv2.COLOR_BGR2HSV)
w = np.array([[[HSV_B / 255, HSV_G / 255, HSV_R / 255]]])
gray_img2 = cv2.convertScaleAbs(np.sum(frame * w, axis=2))

# Darken grayscale image
dark_gray_img2 = np.power(gray_img2.astype('uint16'), HSV_EXP / 10)
max_value = np.max(dark_gray_img2)

dark_gray_img2 = np.round(np.multiply(np.divide(dark_gray_img2, max_value), 255)).astype('uint8')
filtered_image_HSV = cv2.inRange(dark_gray_img2, HSV_THRESHOLD, 255)
cv2.imshow("HSV processed", filtered_image_HSV)

mask_image = np.logical_and(filtered_image_RGB, filtered_image_HSV)
mask_image = (mask_image*255).astype('uint8')
cv2.imshow("Masked image", mask_image)

# Apply gaussian blur to masked image
blurred_image = cv2.GaussianBlur(mask_image, (7, 7), cv2.BORDER_DEFAULT)
cv2.imshow("Blurred image", blurred_image)

#Apply canny edge detection
edge_image = cv2.Canny(blurred_image, 10, 255)
cv2.imshow("Edge image", edge_image)

#Find lanes
threshold = 90
min_line_length = 90
max_line_gap = 40

linesP = cv2.HoughLinesP(edge_image, 1, np.pi / 180, threshold, None, min_line_length, max_line_gap)
if linesP is not None:
    for i in range(0, len(linesP)):
        l = linesP[i][0]
        cv2.line(original_img, (l[0], l[1]), (l[2], l[3]), (0, 255, 0), 3, cv2.LINE_AA)
cv2.imshow("Orginal image with Plines", original_img)
cv2.waitKey(0)



