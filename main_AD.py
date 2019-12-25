import glob
import os
import sys

try:
    sys.path.append(glob.glob('../CARLA_0.9.5/PythonAPI/carla/dist/carla-*%d.%d-%s.egg' % (
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
#from controller import *
import queue

RGB_image = None
SEG_image = None
IM_WIDTH = 1280
IM_HEIGHT = 720
actor_list = []
RGB_img_ready = False
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

def draw_image(surface, image):
    array = np.frombuffer(image.raw_data, dtype=np.dtype("uint8"))
    array = np.reshape(array, (image.height, image.width, 4))
    array = array[:, :, :3]
    array = array[:, :, ::-1]
    image_surface = pygame.surfarray.make_surface(array.swapaxes(0, 1))
    surface.blit(image_surface, (0, 0))

def parse_image(image):
    array = np.frombuffer(image.raw_data, dtype=np.dtype("uint8"))
    array = np.reshape(array, (image.height, image.width, 4))
    array = array[:, :, :3]
    array = array[:, :, ::-1]
    image_surface = pygame.surfarray.make_surface(array.swapaxes(0, 1))
    #pygame.display.get_surface().blit(image_surface, (0,0))

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
    #controller = KeyboardInput(start_in_autopilot)

    clock = pygame.time.Clock()

    blueprint_library = world.get_blueprint_library()

    bp = blueprint_library.filter('model3')[0]
    print(bp)

    spawn_point = random.choice(world.get_map().get_spawn_points())
    print("Spawn point host:", spawn_point)

    vehicle = world.spawn_actor(bp, spawn_point)
    vehicle.set_autopilot(True)  # if you just wanted some NPCs to drive.
    actor_list.append(vehicle)

    #add_test_car(spawn_point)

    # vehicle.apply_control(carla.VehicleControl(throttle=1.0, steer=0.0))


    # https://carla.readthedocs.io/en/latest/cameras_and_sensors
    # get the blueprint for this sensor
    blueprint_rgb = blueprint_library.find('sensor.camera.rgb')
    # change the dimensions of the image
    blueprint_rgb.set_attribute('image_size_x', f'{IM_WIDTH}')
    blueprint_rgb.set_attribute('image_size_y', f'{IM_HEIGHT}')
    blueprint_rgb.set_attribute('fov', '110')

    # Adjust sensor relative to vehicle
    spawn_point = carla.Transform(carla.Location(x=2.5, z=1.3), carla.Rotation(pitch=-0.5))

    # spawn the sensor and attach to vehicle.
    sensor_rgb = world.spawn_actor(blueprint_rgb, spawn_point, attach_to=vehicle)
    
    image_queue = queue.Queue()
    sensor_rgb.listen(image_queue.put)

    # add sensor to list of actors
    actor_list.append(sensor_rgb)

    # do something with this sensor
    #sensor_rgb.listen(lambda data: parse_image(data))
    while True:
        pygame.event.get()
        image = image_queue.get()
        #time.sleep(1) #make function to sleep for 10 seconds
        #clock.tick_busy_loop(60)
        #controller.parse_events(client, world, clock)
        
        #world.tick()
        draw_image(display, image)
        pygame.display.flip()
        clock.tick()
        #text_surface = font.render('% 5d FPS' % clock.get_fps(), True, (255, 255, 255))
        #display.blit(text_surface, (8, 10)))


finally:
    print('destroying actors')
    for actor in actor_list:
        actor.destroy()
    print('done.')
    pygame.quit()
