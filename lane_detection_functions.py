import cv2
import numpy as np
import matplotlib.pyplot as plt

def make_coordiantes(image, line_parameters):
    slope, intercept = line_parameters
    y1 = image.shape[0]
    y2 = int(y1*(3./5))
    x1 = int((y1 - intercept)/slope)
    x2 = int((y2 - intercept)/slope)
    return np.array([x1,y1,x2,y2])

def average_slope_intercept(image, lines):
    ret = []
    left_fit = []
    right_fit = []
    for line in lines:
        x1, y1, x2, y2 = line.reshape(4)
        try:
            parameters = np.polynomial.polynomial.Polynomial.fit((x1,x2), (y1,y2),1)
            parameters = parameters.convert().coef
        except np.linalg.LinAlgError:
            parameters = []
        if len(parameters) == 2:
            slope = parameters[1]
            intercept = parameters[0]
            if slope < 0:
                left_fit.append((slope, intercept))
            else:
                right_fit.append((slope, intercept))
    if(len(left_fit) != 0):
        left_fit_average = np.average(left_fit,axis=0)
        left_line = make_coordiantes(image, left_fit_average)
        ret.append(left_line)
    if(len(right_fit) != 0):
        right_fit_average = np.average(right_fit,axis=0)
        right_line = make_coordiantes(image, right_fit_average)
        ret.append(right_line)
    return np.array(ret)

def canny(image):
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    blur = cv2.GaussianBlur(gray,(5,5),0)
    canny = cv2.Canny(blur,50,150)
    return canny

def display_lines(image, lines):
    line_image = np.zeros_like(image).astype(np.int32)
    if lines is not None:
        for x1, y1, x2, y2 in lines:
            cv2.line(line_image, (x1,y1), (x2,y2), (255,0,0), 10)
    return line_image

def region_of_interest(image):
    height = image.shape[0]
    polygons = np.array([[(100, height), (1200, height), (650, 300)]])
    mask = np.zeros_like(image)
    cv2.fillPoly(mask, polygons, 255)
    masked_image = cv2.bitwise_and(image,mask)
    return masked_image


def overlay_lane_detection(lane_image):
    canny_image = canny(lane_image)
    cropped_image = region_of_interest(canny_image)
    lines = cv2.HoughLinesP(cropped_image, 2, np.pi/180, 100, np.array([]), minLineLength=10, maxLineGap=5)
    if lines is not None:
        averaged_lines = average_slope_intercept(lane_image, lines)
        line_image = display_lines(lane_image, averaged_lines)
        combo_image = cv2.addWeighted(lane_image, 0.8, line_image, 1, 1 )
        return combo_image
    else:
def transform_view(image):
    # define four corners in original image
    src = np.float32([[200, 720], [1100, 720], [520, 450], [700, 450]])
    # define where the corners end up after transformation
    dst = np.float32([[300, 720], [900, 720], [300, 0], [850, 0]])

def transform_view(image, src, dst):
    img_size = (image.shape[1],image.shape[0])
    # Compute perspective tranform from sorce and destination
    M = cv2.getPerspectiveTransform(src, dst)
    # Use transform to warp source image
    warped = cv2.warpPerspective(image, M, img_size)
    return warped

def inverse_transform_view(image, src, dst):
    img_size = (image.shape[1],image.shape[0])
    # Compute perspective tranform from sorce and destination
    M = cv2.getPerspectiveTransform(src, dst)
    # Use transform to warp source image
    warped = cv2.warpPerspective(image, M, img_size)
    return warped