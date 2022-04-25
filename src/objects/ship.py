from dataclasses import dataclass
import math
from mimetypes import init
import time
from typing import Callable
from glm import clamp, sin
import numpy as np

from OpenGL import GL as gl
from utils.geometry import Rect, Rect2, Vec2, Vec3
from utils.logger import LOGGER
from utils.sig import metsig
from app_state import MVPManager
from objects.element import Element
from objects.lines import Lines
from objects.projectile import Projectile

from shader import Shader
import keyboard

from transformation_matrix import Transform
SCREEN_RECT = Rect2(-1, -1, 1, 1)

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
    input_squeeze: float = 1

    enabled = False
    keybinds = {
        "forward": "w",
        "backward": "s",
        "left": "a",
        "right": "d",
        "squeeze": "x",
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
        squeeze = self.keybinds["squeeze"]

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

        if keyboard.is_pressed(squeeze):
            self.input_squeeze = 1.0
        else:
            self.input_squeeze = 0.0

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

        bbox = Element.get_bounding_box(self) / self.transform.scale.xy
        points = [ bbox.bottom_left, bbox.bottom_right, bbox.top_right, bbox.top_left, bbox.bottom_left ]
        points = [ Vec3(point.x, point.y, 0) for point in points ]

        bbox_transform = Transform(
            translation=self.transform.translation.xyz,
            scale=self.transform.scale.xyz,
            rotation=self.transform.rotation.xyz,
        )

        self._debug_bbox = Lines(self.world, points, initial_transform=bbox_transform)

    def _physics_update(self, delta_time: float):
        self.shoot()

        self.controller.process_input()
        if self.controller.input_movement != 0:
            self.move(self.controller.input_movement)
        if self.controller.input_rotation != 0:
        
            ROT_ACCEL = 3.5

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

        SHRINK_RATE = 5
        REGROWTH_RATE = SHRINK_RATE

        if self.controller.input_squeeze != 0:
            MIN_SCALE = 0.8

            t = self.transform
            t.scale *= (1 - self.controller.input_squeeze*(1-MIN_SCALE) * SHRINK_RATE * delta_time)


            if t.scale.x < MIN_SCALE:
                t.scale = Vec3(MIN_SCALE, MIN_SCALE, MIN_SCALE)
        else:
            t = self.transform
            t.scale *= (1 + REGROWTH_RATE * delta_time)
            if t.scale.x > 1:
                t.scale = Vec3(1, 1, 1)

    def _is_out_of_bounds(self) -> bool:
        bbox = Element.get_bounding_box(self)

        if bbox.top_left not in SCREEN_RECT: return True
        # if bbox.top_right not in SCREEN_RECT: return True
        # if bbox.bottom_left not in SCREEN_RECT: return True
        # if bbox.bottom_right not in SCREEN_RECT: return True
        return False

    def move(self, intensity: float = 1):
        super().move(intensity)

        # if self._is_out_of_bounds():
        #     super().move(-intensity)

    def rotate(self, angle: float):
        old_rotation = self.transform.rotation

        super().rotate(angle)

        # if self._is_out_of_bounds():
        #     super().rotate(-angle)

    def shoot(self):
        curr_time = time.time()

        if (curr_time - self._last_shot_time) < SHOOTING_COOLDOWN:
            return

        if not keyboard.is_pressed('space'):
            return

        self._last_shot_time = curr_time

        proj = Projectile.create_from(self)


    def _render(self):
        self._debug_bbox.transform.translation = self.transform.translation.xyz
        self._debug_bbox.transform.rotation = self.transform.rotation.xyz
        self._debug_bbox.transform.scale = self.transform.scale.xyz
        return super()._render()