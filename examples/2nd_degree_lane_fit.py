import sys
sys.path.append('../')
import cv2
import numpy as np
from numpy.polynomial.polynomial import Polynomial as poly
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

SRC = np.float32([[200, 720], [1100, 720], [520, 450], [700, 450]])
DST = np.float32([[300, 720], [900, 720], [300, 0], [850, 0]])
'''
def make_video(screen):

    _image_num = 0
    while True:
	    _image_num += 1
	    str_num = "000" + str(_image_num)
	    file_name = "images/image" + str_num[-4:] + ".jpg"
	    pygame.image.save(screen, file_name)
	    yield
'''
class Game:
    def __init__(self, window_size):
        self.screen = pygame.display.set_mode((window_size[0], window_size[1]))
        self.clock  = pygame.time.Clock()

    def draw_surface(self, surface_array):
        self.screen.blit(surface_array, (0,0))

    def draw_surfaces(self, surface_arrays, fps):
        for surface in surface_arrays:
            self.parse_events()
            self.draw_surface(surface)
            self.update_screen()
            self.update_clock(fps)

    def update_screen(self):
        pygame.display.flip()

    def update_clock(self, fps):
        self.clock.tick_busy_loop(fps)

    def parse_events(self):
        for event in pygame.event.get():
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_ESCAPE:
                    print('Closing Window')
                    sys.exit()
            elif event.type == pygame.QUIT:
                print('Closing Window')
                sys.exit()
        return False

class Rectangle:
    def __init__(self, x_pos=0, y_pos=0, color=COLOR, score=0):
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.color = color
        self.score = score
    
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

def surface_fade(from_surface, to_surface, step):
    surfaces = []
    for i in range(0, 256, step):
        from_surface.set_alpha(256-i)
        to_surface.set_alpha(i)
        average = from_surface.copy()
        average.blit(to_surface, (0, 0))
        surfaces.append(average)
    return surfaces

def overlay_surface(background, foreground, step):
    surfaces = []
    for i in range(0, 256, step):
        background.set_alpha(i)
        overlay = background.copy()
        overlay.blit(foreground, (0, 0))
        surfaces.append(overlay)
    return surfaces

def image_transition(image, src, dst, steps):
    surfaces = []
    first_line  = poly.fit([src[0][0],dst[0][0]], [src[0][1],dst[0][1]], 1)
    second_line = poly.fit([src[1][0],dst[1][0]], [src[1][1],dst[1][1]], 1)
    third_line  = poly.fit([src[2][0],dst[2][0]], [src[2][1],dst[2][1]], 1)
    fourth_line = poly.fit([src[3][0],dst[3][0]], [src[3][1],dst[3][1]], 1)

    first_points    = first_line.linspace(steps)
    second_points   = second_line.linspace(steps)
    third_points    = third_line.linspace(steps)
    fourth_points   = fourth_line.linspace(steps)

    for i in range(1, steps):
        dst = np.float32([[first_points[0][i],first_points[1][i]], [second_points[0][-i],second_points[1][-i]], 
            [third_points[0][-i],third_points[1][-i]], [fourth_points[0][i],fourth_points[1][i]]])
        warped_image = transform_view(image, src, dst)
        image_surface = pygame.surfarray.make_surface(warped_image.swapaxes(0, 1))
        surfaces.append(image_surface)
    return surfaces

def transform_points(src, dst, pts, steps):
    surfaces = []
    surf_array = np.zeros((1280,720,3))
    first_line  = poly.fit([src[0][0],dst[0][0]], [src[0][1],dst[0][1]], 1)
    second_line = poly.fit([src[1][0],dst[1][0]], [src[1][1],dst[1][1]], 1)
    third_line  = poly.fit([src[2][0],dst[2][0]], [src[2][1],dst[2][1]], 1)
    fourth_line = poly.fit([src[3][0],dst[3][0]], [src[3][1],dst[3][1]], 1)

    first_points    = first_line.linspace(steps)
    second_points   = second_line.linspace(steps)
    third_points    = third_line.linspace(steps)
    fourth_points   = fourth_line.linspace(steps)
    for i in range(1,steps):
        dst = np.float32([[first_points[0][-i],first_points[1][-i]], [second_points[0][i],second_points[1][i]], 
            [third_points[0][i],third_points[1][i]], [fourth_points[0][-i],fourth_points[1][-i]]])
        M = cv2.getPerspectiveTransform(src, dst)
        transformed_points = cv2.perspectiveTransform(pts,M)
        surface = pygame.Surface((1280, 720))

        pygame.draw.polygon(surface, (0,130,0), np.squeeze(transformed_points, axis=0))
        surfaces.append(surface)
    return surfaces

pygame.init()

game = Game((1280,720))
image = cv2.imread('00004746.png')

img_size = (image.shape[0],image.shape[1], 3)

WINDOW_SIZE_Y = int(np.floor(img_size[0]/NUMBER_OF_WINDOWS))

canny_image = canny(image)
warped_canny = transform_view(canny_image, SRC, DST)

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

best_rects = []

birds_eye_view = image_transition(image, SRC, DST, 300)
game.draw_surfaces(birds_eye_view, 60)

three_channel_warped_canny = np.zeros(img_size)
three_channel_warped_canny[:,:,0] = warped_canny[:,:]
three_channel_warped_canny[:,:,1] = warped_canny[:,:]
three_channel_warped_canny[:,:,2] = warped_canny[:,:]
image_surface_1 = pygame.surfarray.make_surface(three_channel_warped_canny.swapaxes(0, 1))

fade_to_canny = surface_fade(birds_eye_view[-1], image_surface_1, 1)
game.draw_surfaces(fade_to_canny, 60)

image_surface = pygame.surfarray.make_surface(coloured_lines.swapaxes(0, 1))
fade_to_colour = surface_fade(image_surface_1, image_surface, 1)
game.draw_surfaces(fade_to_colour, 60)

for line in range(2):
    x_pixel = 0 + (IMAGE_MIDDLE_POINT*line)
    y_pixel = 0
    for window in range(NUMBER_OF_WINDOWS):
        current_best_rect = Rectangle(x_pixel, y_pixel, (0, 255, 128))
        while (x_pixel + WINDOW_SIZE_X) < IMAGE_MIDDLE_POINT+(IMAGE_MIDDLE_POINT*line):
            rect = Rectangle(x_pixel, y_pixel)
            game.parse_events()
            game.screen.blit(image_surface, (0, 0))
            get_area_brightness(rect, warped_canny)
            if current_best_rect.score < rect.score:
                rect.color = (0, 255, 128)
                current_best_rect = rect
            draw_multiple_rects(list(best_rects)+[rect, current_best_rect], game.screen)
            x_pixel += STEP_SIZE
            pygame.display.flip()
            game.clock.tick_busy_loop(60)

        x_pixel = 0 + (IMAGE_MIDDLE_POINT*line)
        y_pixel += WINDOW_SIZE_Y
        best_rects.append(current_best_rect)
game.screen.blit(image_surface, (0, 0))     
draw_multiple_rects(list(best_rects), game.screen)
pygame.display.flip()
game.clock.tick_busy_loop(1)

rect_surface = pygame.display.get_surface()

left_line_y_indices, left_line_x_indices = extract_pixels_from_image(best_rects[:NUMBER_OF_WINDOWS], warped_canny)
right_line_y_indices, right_line_x_indices = extract_pixels_from_image(best_rects[NUMBER_OF_WINDOWS:], warped_canny)

left_line_fit_coef = np.polynomial.polynomial.Polynomial.fit(left_line_y_indices, left_line_x_indices, 2)
right_line_fit_coef = np.polynomial.polynomial.Polynomial.fit(right_line_y_indices, right_line_x_indices, 2)


left_line_fit = left_line_fit_coef.linspace(720)
right_line_fit = right_line_fit_coef.linspace(720)

line_image = np.zeros_like(coloured_lines).astype(np.int8)
pts_left = np.array([np.transpose(np.vstack([left_line_fit[1], left_line_fit[0]]))])
pts_right = np.array([np.flipud(np.transpose(np.vstack([right_line_fit[1], right_line_fit[0]])))])
pts = np.hstack((pts_left, pts_right))

cv2.fillPoly(line_image, np.int_([pts]), (0,255, 0))
lane_fade = surface_fade(rect_surface, pygame.surfarray.make_surface(line_image.swapaxes(0, 1)), 1)
game.draw_surfaces(lane_fade, 60)

line_image = line_image.astype(np.float32)
normal_view = transform_points(DST, SRC, pts, 300)
game.draw_surfaces(normal_view, 60)

lane_overlay = normal_view[-1].convert()
lane_overlay.set_alpha(100)
lane_overlay.set_colorkey((0,0,0))

camera_surface = pygame.surfarray.make_surface(image.swapaxes(0, 1))
lane_detection_result = overlay_surface(camera_surface, lane_overlay, 1)
game.draw_surfaces(lane_detection_result, 60)

pygame.quit()