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
import argparse

try:
    import pygame
    from pygame.locals import K_p
except ImportError:
    raise RuntimeError('cannot import pygame, make sure pygame package is installed')


class KeyboardInput(object):
    def __init__(self, start_in_autopilot):
        self._autopilot_enabled = start_in_autopilot
    
    def parse_events(self, player):
        for event in pygame.event.get():
            if event.type == pygame.KEYUP:
                print('!!!!! KEY PRESSED !!!!!')
                if event.key == K_p:
                    self._autopilot_enabled = not self._autopilot_enabled
                    player.set_autopilot(self._autopilot_enabled)
                    return 1
                elif event.key == pygame.K_ESCAPE:
                    return 2
            elif event.type == pygame.QUIT:
                return 2
            return 0