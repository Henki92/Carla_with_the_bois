import cv2
import numpy as np
import matplotlib.pyplot as plt

# Get image from carla but for now just take a png file
original_img = cv2.imread('example.jpg', cv2.IMREAD_ANYCOLOR)
print("img type is", type(original_img))
# Display image
cv2.imshow('Original image', original_img)
cv2.waitKey(0)

# Define ROI and remove everything else
# TODO HERE

# Convert orignal to greyscale
# We want yellow and white to be brighter, this is the lane colors in carla
# OPENCV does BGR format
w = np.array([[[0.1, 0.45,  0.45]]])
gray_img = cv2.convertScaleAbs(np.sum(original_img*w, axis=2))
cv2.imshow('Processed image', gray_img)
cv2.waitKey(0)

# Darken grayscale image
dark_gray_img =np.power(gray_img.astype('uint16'), 1.1)
max_value = np.max(dark_gray_img)
print("Max values in image before and after is: ", np.max(gray_img), np.max(dark_gray_img))
dark_gray_img = np.multiply(np.round(np.divide(dark_gray_img, max_value)), 255).astype('uint8')
print("Max value in image after division: ", np.max(dark_gray_img))
cv2.imshow('Processed image', dark_gray_img)
cv2.waitKey(0)

# Do the same for HSV colorspace
HSV_img = cv2.cvtColor(original_img, cv2.COLOR_BGR2HSV);
cv2.imshow('Processed image', HSV_img)
cv2.waitKey(0)

# Convert HSV to greyscale
# We want yellow and white to be brighter, this is the lane colors in carla
# OPENCV does BGR format
w = np.array([[[0.1, 0.45,  0.45]]])
gray_img2 = cv2.convertScaleAbs(np.sum(HSV_img*w, axis=2))
cv2.imshow('Processed image', gray_img2)
cv2.waitKey(0)

# Darken grayscale image
dark_gray_img2 = np.power(gray_img2.astype('uint16'), 1.1)
max_value = np.max(dark_gray_img2)
print("Max values in image before and after is: ", np.max(gray_img2), np.max(dark_gray_img2))
dark_gray_img2 = np.multiply(np.round(np.divide(dark_gray_img2, max_value)), 255).astype('uint8')
print("Max value in image after division: ", np.max(dark_gray_img2))
cv2.imshow('Processed image', dark_gray_img2)
cv2.waitKey(0)


