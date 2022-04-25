from dataclasses import dataclass
import math
from mimetypes import init
import time
from typing import Callable
from glm import clamp
import numpy as np

from OpenGL import GL as gl
from utils.sig import metsig
from app_state import MVPManager
from objects.element import Element
from objects.projectile import Projectile

from shader import Shader
import keyboard

BASE_SIZE = 1/16 * (1 - (-1))

SHOOTING_COOLDOWN = 0.2

TRANSLATION_STEP = 0.04
ROTATION_STEP = 2*math.pi/360 * 5

@dataclass
class ShipController:
    """
    This class is used to store the movement of the ship.
    User input is stored in this class. (in the current frame)
    """
    input_movement: float = 0
    input_rotation: float = 0
    enabled = False
    keybinds = {
        "forward": "w",
        "backward": "s",
        "left": "a",
        "right": "d",
    }

    def enable(self):
        self.enabled = True
    def disable(self):
        self.enabled = False

    def process_input(self):
        trans_multiplier = 1
        rot_multiplier = 1
        if not self.enabled:
            return
        forward = self.keybinds["forward"]
        backward = self.keybinds["backward"]
        left = self.keybinds["left"]
        right = self.keybinds["right"]

        if keyboard.is_pressed('shift'):
            trans_multiplier *= 2
            rot_multiplier *= 2
        elif keyboard.is_pressed('ctrl'):
            trans_multiplier *= 0.5
            rot_multiplier *= 0.5

        if keyboard.is_pressed(forward):
            self.input_movement = trans_multiplier * TRANSLATION_STEP
        elif keyboard.is_pressed(backward):
            self.input_movement = -trans_multiplier * TRANSLATION_STEP
        else:
            self.input_movement = 0

        if keyboard.is_pressed(left):
            self.input_rotation = rot_multiplier * ROTATION_STEP
        elif keyboard.is_pressed(right):
            self.input_rotation = -rot_multiplier * ROTATION_STEP
        else:
            self.input_rotation = 0


@dataclass(init=False)
class Ship(Element):
    # speed: float = 1
    energy: float = 1 # [1, 2]: indicates glow intensity
    ship_len = 0.4
    _rotation_intensity = 0

    def _init_vertices(self):
        self._vertices = [
            *(-0.1, -0.1, 0.0),
            *(0.1, -0.1, 0.0),
            *(-0.1, 0.1, 0.0),
            *(0.1, -0.1, 0.0),
            *(0.1, 0.1, 0.0),
            *(-0.1, 0.1, 0.0),
            *(-0.1, 0.1, 0.0),
            *(0.1, 0.1, 0.0),
            *(0 , 0.3, 0.0),
        ]

    @metsig(Element.__init__)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.controller = ShipController()
        self._last_shot_time = time.time()

    def _physics_update(self, delta_time: float):
        self.shoot()

        self.controller.process_input()
        if self.controller.input_movement != 0:
            self.move(self.controller.input_movement)
        if self.controller.input_rotation != 0:
            ROT_ACCEL = 3.5
            print(f'rotation: {self.controller.input_rotation}, intensity: {self._rotation_intensity}')

            if self._rotation_intensity * self.controller.input_rotation < 0:
                self._rotation_intensity = 0 # Turning direction changed

            self._rotation_intensity += self.controller.input_rotation * delta_time * ROT_ACCEL

            inp_abs = abs(self.controller.input_rotation)
            min_rot = -inp_abs
            max_rot = inp_abs
            self._rotation_intensity = clamp(self._rotation_intensity, min_rot, max_rot)

            self.rotate(self._rotation_intensity)
        else:
            self._rotation_intensity = 0
            pass

    def shoot(self):
        curr_time = time.time()

        if (curr_time - self._last_shot_time) < SHOOTING_COOLDOWN:
            return

        if not keyboard.is_pressed('space'):
            return

        self._last_shot_time = curr_time

        proj = Projectile.create_from(self)