from __future__ import print_function
import cv2 as cv
import argparse
import numpy as np

max_value = 255
B_value = round(255/3)
G_value = round(255/3)
R_value = round(255/3)
exponent_value = 10
threshold_value = 0
window_capture_name = 'Video Capture'
window_detection_name = 'Object Detection'


def B_value_change(val):
    global B_value
    B_value = val
    cv.setTrackbarPos("B", window_detection_name, val)


def G_value_change(val):
    global G_value
    G_value = val
    cv.setTrackbarPos("G", window_detection_name, val)


def R_value_change(val):
    global R_value
    R_value = val
    cv.setTrackbarPos("R", window_detection_name, val)


def exp_value_change(val):
    global exponent_value
    exponent_value = val
    cv.setTrackbarPos("Exponent", window_detection_name, val)


def threshold_value_change(val):
    global threshold_value
    threshold_value = val
    cv.setTrackbarPos("Threshold", window_detection_name, val)


cv.namedWindow(window_capture_name)
cv.namedWindow(window_detection_name)
cv.createTrackbar("B", window_detection_name, B_value, max_value, B_value_change)
cv.createTrackbar("G", window_detection_name, G_value, max_value, G_value_change)
cv.createTrackbar("R", window_detection_name, R_value, max_value, R_value_change)
cv.createTrackbar("Exponent", window_detection_name, exponent_value, 50, exp_value_change)
cv.createTrackbar("Threshold", window_detection_name, threshold_value, 255, threshold_value_change)

frame = cv.imread('example.jpg', cv.IMREAD_ANYCOLOR)
#frame = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
cv.imshow(window_capture_name, frame)

while True:

    w = np.array([[[B_value/255, G_value/255, R_value/255]]])
    print(B_value, G_value, R_value)
    gray_img2 = cv.convertScaleAbs(np.sum(frame * w, axis=2))

    # Darken grayscale image
    dark_gray_img2 = np.power(gray_img2.astype('uint16'), exponent_value/10)
    max_value = np.max(dark_gray_img2)
    print("Max value:", max_value, "Exponent:", exponent_value)

    dark_gray_img2 = np.round(np.multiply(np.divide(dark_gray_img2, max_value), 255)).astype('uint8')
    filtered_image = cv.inRange(dark_gray_img2, threshold_value, 255)
    cv.imshow(window_detection_name, filtered_image)

    key = cv.waitKey(30)
    if key == ord('q') or key == 27:
        break

