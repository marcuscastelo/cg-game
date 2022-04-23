from dataclasses import dataclass
import math
from mimetypes import init
import time
from typing import Callable
import numpy as np

from OpenGL import GL as gl
from utils.sig import metsig
from app_state import MVPManager
from objects.element import Element
from objects.projectile import Projectile

from shader import Shader
import keyboard

BASE_SIZE = 1/16 * (1 - (-1))

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
        if not self.enabled:
            return

        TRANSLATION_STEP = 0.04
        ROTATION_STEP = 2*math.pi/360 * 5
        forward = self.keybinds["forward"]
        backward = self.keybinds["backward"]
        left = self.keybinds["left"]
        right = self.keybinds["right"]

        if keyboard.is_pressed('shift'):
            TRANSLATION_STEP *= 2
            ROTATION_STEP *= 2
        elif keyboard.is_pressed('ctrl'):
            TRANSLATION_STEP *= 0.5
            ROTATION_STEP *= 0.5

        if keyboard.is_pressed(forward):
            self.input_movement = TRANSLATION_STEP
        elif keyboard.is_pressed(backward):
            self.input_movement = -TRANSLATION_STEP
        else:
            self.input_movement = 0

        if keyboard.is_pressed(left):
            self.input_rotation = ROTATION_STEP
        elif keyboard.is_pressed(right):
            self.input_rotation = -ROTATION_STEP
        else:
            self.input_rotation = 0


@dataclass(init=False)
class Ship(Element):
    # speed: float = 1
    energy: float = 1 # [1, 2]: indicates glow intensity
    ship_len = 0.4

    def _init_vertices(self):
        self._vertices = [
            *(-0.1, 0.0, 0.0),
            *(0.1, 0.0, 0.0),
            *(-0.1, 0.2, 0.0),
            *(0.1, 0.0, 0.0),
            *(0.1, 0.2, 0.0),
            *(-0.1, 0.2, 0.0),
            *(-0.1, 0.2, 0.0),
            *(0.1, 0.2, 0.0),
            *(0 , 0.4, 0.0),
        ]

    @metsig(Element.__init__)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.controller = ShipController()
        self._last_shot_time = time.time()
        self._projectiles: list[Element] = []

    def _physic_update(self):
        self.shoot()

        self.controller.process_input()
        if self.controller.input_movement != 0:
            self.move(self.controller.input_movement)
        if self.controller.input_rotation != 0:
            self.rotate(self.controller.input_rotation)

    def render(self):
        projs_to_remove = []
        for proj in self._projectiles:
            proj.render()
            # if proj.is_out_of_bounds():
            #     projs_to_remove.append(proj)

        # for proj in projs_to_remove:
        #     self._projectiles.remove(proj)

        return super().render()

    def shoot(self):
        curr_time = time.time()

        if (curr_time - self._last_shot_time) < 2:
            return

        if not keyboard.is_pressed('space'):
            return

        self._last_shot_time = curr_time

        proj = Projectile.create_from(self)
        # other = Ship((self.x, self.y, self.z))
        # other.controller.disable()
        # other.controller.input_movement = 0.035
        # other.angle = self.angle
        # other._last_shot_time = 10000000000000000000000000

        self._projectiles.append(proj)