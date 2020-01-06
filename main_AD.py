import glob
import os
import sys

try:
    sys.path.append(glob.glob('../CARLA_0.9.5/PythonAPI/carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
    sys.path.append('Lane_detection')
    sys.path.append('Object_detection')
except IndexError:
    pass

import carla

import random
import time
import numpy as np
import cv2
import threading 
from lane_detection_functions import overlay_lane_detection
from Obj_2 import find_bounding_boxes
from controller import *
import queue
import pygame

RGB_image = None
SEG_image = None
''' 
Possible merge issue with new image size
IM_WIDTH = 640
IM_HEIGHT = 480
'''
IM_WIDTH = 1280
IM_HEIGHT = 720
actor_list = []
RGB_img_ready = False
bounding_box_ready = False
bounding_box = []

def save_OD_screenshots(SEG_img):
    global bounding_box, bounding_box_ready, SEG_image, RGB_image
    i = np.array(SEG_img.raw_data)
    i2 = i.reshape((IM_HEIGHT, IM_WIDTH, 4))
    i3 = i2[:, :, :3]
    # Draw bounding box
    OD_object_list = find_bounding_boxes(i3)
    bounding_box_ready = True
    # Draw bounding boxes
    for obj in OD_object_list:
        result = cv2.rectangle(RGB_image, (min(obj.x), min(obj.y)), (max(obj.x), max(obj.y)), (0, 0, 255), 3,
                               cv2.LINE_AA)

    cv2.imshow("Result image", RGB_image)
    cv2.waitKey(0)

    #save_screenshot()


def save_screenshot():
    global SEG_image, RGB_image, bounding_box, bounding_box_ready, RGB_img_ready
    if bounding_box_ready and RGB_img_ready:
        #result = cv2.rectangle(RGB_image, (bounding_box[0], bounding_box[2]), (bounding_box[1], bounding_box[3]), (0, 0, 255), 3, cv2.LINE_AA)
        cv2.imwrite('Object_detection.png', SEG_image)
        cv2.waitKey(0)
        #print("SAVE SCREENSHOT FUNCTION")


def add_test_car(spawn_point):
    spawn_point_2 = spawn_point
    if 10 > spawn_point.rotation.yaw > -10:
        spawn_point_2.location.x = spawn_point_2.location.x + 8
    elif 100 > spawn_point.rotation.yaw > 80:
        spawn_point_2.location.y = spawn_point_2.location.y + 8
    elif -80 > spawn_point.rotation.yaw > -100:
        spawn_point_2.location.y = spawn_point_2.location.y - 8
    else:
        spawn_point_2.location.x = spawn_point_2.location.x - 8
    print("Spawn point test car:", spawn_point_2)
    vehicle2 = world.spawn_actor(bp, spawn_point_2)
    vehicle2.set_autopilot(True)  # if you just wanted some NPCs to drive.w
    actor_list.append(vehicle2)


def add_test_car2(spawn_point):
    spawn_point_2 = spawn_point
    if 10 > spawn_point.rotation.yaw > -10:
        spawn_point_2.location.x = spawn_point_2.location.x + 8
        spawn_point_2.location.y = spawn_point_2.location.y + 8
    elif 100 > spawn_point.rotation.yaw > 80:
        spawn_point_2.location.x = spawn_point_2.location.x + 8
        spawn_point_2.location.y = spawn_point_2.location.y + 8
    elif -80 > spawn_point.rotation.yaw > -100:
        spawn_point_2.location.x = spawn_point_2.location.x + 8
        spawn_point_2.location.y = spawn_point_2.location.y - 8
    else:
        spawn_point_2.location.y = spawn_point_2.location.y - 8
        spawn_point_2.location.x = spawn_point_2.location.x - 8
    print("Spawn point test car:", spawn_point_2)
    vehicle2 = world.spawn_actor(bp, spawn_point_2)
    vehicle2.set_autopilot(True)  # if you just wanted some NPCs to drive.w
    actor_list.append(vehicle2)

def draw_image(surface, image):
    array = np.frombuffer(image.raw_data, dtype=np.dtype("uint8"))
    array = np.reshape(array, (image.height, image.width, 4))
    array = array[:, :, :3]
    array = array[:, :, ::-1]
    array = overlay_lane_detection(array)
    image_surface = pygame.surfarray.make_surface(array.swapaxes(0, 1))
    surface.blit(image_surface, (0, 0))

try:    
    pygame.init()
    pygame.font.init()

    client = carla.Client('localhost', 2000)
    client.set_timeout(5.0)

    world = client.get_world()
    pygame_width = 1280
    pygame_height = 720
    display = pygame.display.set_mode(
            (pygame_width, pygame_height),
            pygame.HWSURFACE | pygame.DOUBLEBUF)

    # Add input key parser 
    start_in_autopilot = True
    controller = KeyboardInput(start_in_autopilot)

    clock = pygame.time.Clock()

    blueprint_library = world.get_blueprint_library()

    bp = blueprint_library.filter('model3')[0]
    print(bp)

    spawn_point = random.choice(world.get_map().get_spawn_points())
    print("Spawn point host:", spawn_point)

    vehicle = world.spawn_actor(bp, spawn_point)
    vehicle.set_autopilot(True)  # if you just wanted some NPCs to drive.
    actor_list.append(vehicle)

    add_test_car(spawn_point)
    #add_test_car2(spawn_point)

    # vehicle.apply_control(carla.VehicleControl(throttle=1.0, steer=0.0))


    # https://carla.readthedocs.io/en/latest/cameras_and_sensors
    # get the blueprint for this sensor
    blueprint_rgb = blueprint_library.find('sensor.camera.rgb')
    # change the dimensions of the image
    blueprint_rgb.set_attribute('image_size_x', f'{IM_WIDTH}')
    blueprint_rgb.set_attribute('image_size_y', f'{IM_HEIGHT}')
    blueprint_rgb.set_attribute('fov', '110')

    # get the blueprint for this sensor
    blueprint_seg = blueprint_library.find('sensor.camera.semantic_segmentation')
    # change the dimensions of the image
    blueprint_seg.set_attribute('image_size_x', f'{IM_WIDTH}')
    blueprint_seg.set_attribute('image_size_y', f'{IM_HEIGHT}')
    blueprint_seg.set_attribute('fov', '110')

    # Adjust sensor relative to vehicle
    spawn_point = carla.Transform(carla.Location(x=2.5, z=1.3), carla.Rotation(pitch=-0.5))

    # spawn the sensor and attach to vehicle.
    sensor_rgb = world.spawn_actor(blueprint_rgb, spawn_point, attach_to=vehicle)
    # spawn the sensor and attach to vehicle.
    sensor_seg = world.spawn_actor(blueprint_seg, spawn_point, attach_to=vehicle)
    
    image_queue = queue.Queue()
    sensor_rgb.listen(image_queue.put)

    # add sensor to list of actors
    actor_list.append(sensor_rgb)
    # add sensor to list of actors
    actor_list.append(sensor_seg)
    # do something with this sensor
    sensor_seg.listen(lambda data: save_OD_screenshots(data))
    # create a timer
    timer = threading.Timer(10.0, save_screenshot)
    timer.start()
    while True:
        pygame.event.get()
        try:
            image = image_queue.get()
        except queue.Empty:
            print("Queue is empty")
        clock.tick_busy_loop(30)
        if controller.parse_events(vehicle) == 2:
            break
        print(image)
        draw_image(display, image)
        pygame.display.flip()
        clock.tick()

finally:
    timer.cancel() 
    print('destroying actors')
    for actor in actor_list:
        actor.destroy()
    print('done.')
    pygame.quit()
