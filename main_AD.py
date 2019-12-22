import glob
import os
import sys

try:
    sys.path.append(glob.glob('CARLA_0.9.5/PythonAPI/carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
    sys.path.append('Lane_detection')
except IndexError:
    pass

import carla

import random
import time
import numpy as np
import cv2
from lane_detection_functions import overlay_lane_detection


RGB_image = None
SEG_image = None
IM_WIDTH = 1280
IM_HEIGHT = 720
actor_list = []
RGB_img_ready = False
bounding_box_ready = False
bounding_box = []


def process_img(image):
    global RGB_image, RGB_img_ready
    i = np.array(image.raw_data)
    i2 = i.reshape((IM_HEIGHT, IM_WIDTH, 4))
    i3 = i2[:, :, :3]
    # Do processing
    result = overlay_lane_detection(i3)
    cv2.imshow("Lane detection", result)
    cv2.waitKey(250)
    RGB_image = i3
    RGB_img_ready = True


def save_OD_screenshots(SEG_img):
    global bounding_box, bounding_box_ready
    i = np.array(SEG_img.raw_data)
    i2 = i.reshape((IM_HEIGHT, IM_WIDTH, 4))
    i3 = i2[:, :, 2:3]
    # Find interesting area
    list_of_pixel_coord_with_cars = np.where(i3 == 10)
    #print(list_of_pixel_coord_with_cars)
    coord = list(zip(list_of_pixel_coord_with_cars[0], list_of_pixel_coord_with_cars[1]))
    #print(coord)
    # iterate over the list of coordinates
    x_min = np.min(list_of_pixel_coord_with_cars[1])
    x_max = np.max(list_of_pixel_coord_with_cars[1])
    y_min = np.max(list_of_pixel_coord_with_cars[0])
    y_max = np.min(list_of_pixel_coord_with_cars[0])
    #for cord in coord:
    #    print(cord)
    # Draw bounding box
    bounding_box = [x_min, x_max, y_min, y_max]
    bounding_box_ready = True


def save_screenshot():
    global RGB_image, bounding_box
    result = cv2.rectangle(RGB_image, (bounding_box[0], bounding_box[2]), (bounding_box[1], bounding_box[3]), (0, 0, 255), 3, cv2.LINE_AA)
    cv2.imshow("Object detection", result)
    cv2.waitKey(250)
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
    vehicle2.set_autopilot(True)  # if you just wanted some NPCs to drive.
    actor_list.append(vehicle2)


try:
    client = carla.Client('localhost', 2000)
    client.set_timeout(5.0)

    world = client.get_world()

    blueprint_library = world.get_blueprint_library()

    bp = blueprint_library.filter('model3')[0]
    print(bp)

    spawn_point = random.choice(world.get_map().get_spawn_points())
    print("Spawn point host:", spawn_point)

    vehicle = world.spawn_actor(bp, spawn_point)
    vehicle.set_autopilot(True)  # if you just wanted some NPCs to drive.
    actor_list.append(vehicle)

    add_test_car(spawn_point)

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

    # add sensor to list of actors
    actor_list.append(sensor_rgb)
    # add sensor to list of actors
    actor_list.append(sensor_seg)

    # do something with this sensor
    sensor_rgb.listen(lambda data: process_img(data))
    #sensor_seg.listen(lambda data: save_OD_screenshots(data))
    while True:
        #time.sleep(1) #make function to sleep for 10 seconds
        if bounding_box_ready and RGB_img_ready:
            save_screenshot()

finally:
    print('destroying actors')
    for actor in actor_list:
        actor.destroy()
    print('done.')
