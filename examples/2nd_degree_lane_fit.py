import sys
sys.path.append('../')
import cv2
import numpy as np
from lane_detection_functions import *
import matplotlib.pyplot as plt
import pygame

NUMBER_OF_WINDOWS       = 9
WINDOW_SIZE_X           = 100
IMAGE_MIDDLE_POINT      = 640
STEP_SIZE               = 20
ZERO_MASK               = np.zeros((720, IMAGE_MIDDLE_POINT))
ONE_MASK                = np.ones((720, IMAGE_MIDDLE_POINT))
LEFT_MASK               = np.concatenate((ONE_MASK, ZERO_MASK), axis=1) > 0
RIGHT_MASK              = np.concatenate((ZERO_MASK, ONE_MASK), axis=1) > 0
COLOR                   = (0, 128, 255)
RECTANLE_BORDER_WIDTH   = 5

best_window_left    = []
best_window_right   = []

class Rectangle:
    def __init__(self, x_pos=0, y_pos=0, color=COLOR, score=0):
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.color = color
        self.score = score
    

def parse_events():
    for event in pygame.event.get():
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_ESCAPE:
                print('Closing Window')
                return True
        elif event.type == pygame.QUIT:
            print('Closing Window')
            return True
    return False

def draw_rect(rect, surface):               
    pygame.draw.rect(surface, rect.color, pygame.Rect(rect.x_pos, rect.y_pos, WINDOW_SIZE_X, 5))
    pygame.draw.rect(surface, rect.color, pygame.Rect(rect.x_pos, rect.y_pos, 5, WINDOW_SIZE_Y))
    pygame.draw.rect(surface, rect.color, pygame.Rect(rect.x_pos+WINDOW_SIZE_X-5, rect.y_pos, 5, WINDOW_SIZE_Y))
    pygame.draw.rect(surface, rect.color, pygame.Rect(rect.x_pos, rect.y_pos+WINDOW_SIZE_Y-5, WINDOW_SIZE_X, 5))

def get_sub_image(rect, image):
    return image[rect.y_pos:(rect.y_pos+WINDOW_SIZE_Y),rect.x_pos:(rect.x_pos+WINDOW_SIZE_X)]

def get_area_brightness(rect, image):
    area = get_sub_image(rect, image)
    brightness = np.sum(area)
    rect.score = brightness

def draw_multiple_rects(rects, surface):
    for rect in rects:
        draw_rect(rect, surface)

def extract_pixels_from_image(windows, image):
    y_indices = np.array([])
    x_indices = np.array([])
    for window in windows:
        pixels_of_interest = get_sub_image(window, image)
        non_zero_entries = pixels_of_interest.nonzero()
        y_indices = np.append(y_indices, non_zero_entries[0]+window.y_pos)
        x_indices = np.append(x_indices, non_zero_entries[1]+window.x_pos)
    return y_indices, x_indices

pygame.init()

image = cv2.imread('00004746.png')
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
img_size = (image.shape[0],image.shape[1], 3)

WINDOW_SIZE_Y = int(np.floor(img_size[0]/NUMBER_OF_WINDOWS))

canny_image = canny(image)
warped_canny = transform_view(canny_image)

red_mask    = (warped_canny > 0) & LEFT_MASK
blue_mask   = (warped_canny > 0) & RIGHT_MASK

opacity = warped_canny/255

coloured_lines  = np.zeros(img_size)

coloured_lines[red_mask] = [255, 0, 0]
coloured_lines[blue_mask] = [0, 255, 0]

coloured_lines[:,:,0] *= opacity
coloured_lines[:,:,1] *= opacity

histogram = np.sum(warped_canny[warped_canny.shape[0]//2:,:], axis=0)

color = (0, 128, 255)

#pygame.display.flip()
#clock.tick()
best_rects = []

image_surface = pygame.surfarray.make_surface(coloured_lines.swapaxes(0, 1))
for line in range(2):
    x_pixel = 0 + (IMAGE_MIDDLE_POINT*line)
    y_pixel = 0
    for window in range(NUMBER_OF_WINDOWS):
        current_best_rect = Rectangle(x_pixel, y_pixel, (0, 255, 128))
        while (x_pixel + WINDOW_SIZE_X) < IMAGE_MIDDLE_POINT+(IMAGE_MIDDLE_POINT*line):
            rect = Rectangle(x_pixel, y_pixel)
            if parse_events():
                break
            screen.blit(image_surface, (0, 0))
            get_area_brightness(rect, warped_canny)
            if current_best_rect.score < rect.score:
                rect.color = (0, 255, 128)
                current_best_rect = rect
            draw_multiple_rects(list(best_rects)+[rect, current_best_rect], screen)
            x_pixel += STEP_SIZE
            pygame.display.flip()
            clock.tick_busy_loop(30)
            clock.tick()

        x_pixel = 0 + (IMAGE_MIDDLE_POINT*line)
        y_pixel += WINDOW_SIZE_Y
        best_rects.append(current_best_rect)
pygame.quit()
left_line_y_indices, left_line_x_indices = extract_pixels_from_image(best_rects[:NUMBER_OF_WINDOWS], warped_canny)
right_line_y_indices, right_line_x_indices = extract_pixels_from_image(best_rects[NUMBER_OF_WINDOWS:], warped_canny)

print(left_line_x_indices, left_line_y_indices)

left_line_fit_coef = np.polynomial.polynomial.Polynomial.fit(left_line_y_indices, left_line_x_indices, 2)
right_line_fit_coef = np.polynomial.polynomial.Polynomial.fit(right_line_y_indices, right_line_x_indices, 2)
#left_line_fit_coef.domain = [0,719]
#right_line_fit_coef.domain = [0, 719]
#print(type(left_line_fit_coef), right_line_fit_coef.domain)
#left_line_fit_coef = left_line_fit_coef.convert().coef
#right_line_fit_coef = right_line_fit_coef.convert().coef


y_values = np.linspace(0, warped_canny.shape[0]-1, warped_canny.shape[0])
#left_line_fit = left_line_fit_coef[0] *  y_values ** 2 + left_line_fit_coef[1] * y_values + left_line_fit_coef[2]
#right_line_fit = right_line_fit_coef[0] *  y_values ** 2 + right_line_fit_coef[1] * y_values + right_line_fit_coef[2]

left_line_fit = left_line_fit_coef.linspace(720)
right_line_fit = right_line_fit_coef.linspace(720)
#print(left_line_fit)
line_image = np.zeros_like(coloured_lines).astype(np.int8)

pts_left = np.array([np.transpose(np.vstack([left_line_fit[1], left_line_fit[0]]))])
pts_right = np.array([np.flipud(np.transpose(np.vstack([right_line_fit[1], right_line_fit[0]])))])
pts = np.hstack((pts_left, pts_right))

cv2.fillPoly(line_image, np.int_([pts]), (0,255, 0))
print(type(line_image), line_image.shape, np.dtype(line_image[0][0][0]))
unwarped_line_image = inverse_transform_view(line_image.astype(np.float32))
print(type(unwarped_line_image), unwarped_line_image.shape, np.dtype(unwarped_line_image[0][0][0]))
#image = image.astype(np.float32)
print(type(image), image.shape, np.dtype(image[0][0][0]))
combo = cv2.addWeighted(image, 0.8, unwarped_line_image.astype(np.uint8), 1, 1 )
cv2.imshow('image',combo)
cv2.waitKey(0)  
cv2.destroyAllWindows()