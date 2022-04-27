from dataclasses import dataclass
import math
import time
from glm import clamp
from OpenGL import GL as gl

from utils.geometry import Rect2, Vec2, Vec3, VecN
from utils.sig import metsig
from objects.element import Element, Vertex, VertexSpecification
from objects.projectile import Projectile

from input.input_system import INPUT_SYSTEM as IS

import numpy as np

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

        if IS.is_pressed('shift'):
            trans_multiplier *= 2
            rot_multiplier *= 2
        elif IS.is_pressed('ctrl'):
            trans_multiplier *= 0.5
            rot_multiplier *= 0.5

        if IS.is_pressed(forward):
            self.input_movement = trans_multiplier * TRANSLATION_STEP
        elif IS.is_pressed(backward):
            self.input_movement = -trans_multiplier * TRANSLATION_STEP
        else:
            self.input_movement = 0

        if IS.is_pressed(left):
            self.input_rotation = rot_multiplier * ROTATION_STEP
        elif IS.is_pressed(right):
            self.input_rotation = -rot_multiplier * ROTATION_STEP
        else:
            self.input_rotation = 0

        if IS.is_pressed(squeeze):
            self.input_squeeze = 1.0
        else:
            self.input_squeeze = 0.0

@dataclass(init=False)
class Ship(Element):
    # speed: float = 1
    energy: float = 1 # [1, 2]: indicates glow intensity
    ship_len = 0.4
    _rotation_intensity = 0
    _was_t_pressed = False

    def _create_vertex_buffer(self) -> VertexSpecification:
        return VertexSpecification([
            Vertex(Vec3(-0.1, -0.1, 0.0), Vec2(0, 0)),
            Vertex(Vec3(0.1, -0.1, 0.0), Vec2(1, 0)),
            Vertex(Vec3(-0.1, 0.1, 0.0), Vec2(0, +2/4)),
            
            Vertex(Vec3(0.1, -0.1, 0.0), Vec2(+1, 0)),
            Vertex(Vec3(0.1, 0.1, 0.0), Vec2(+1, +2/4)),
            Vertex(Vec3(-0.1, 0.1, 0.0), Vec2(0, +2/4)),

            Vertex(Vec3(-0.1, 0.1, 0.0), Vec2(0, +2/4)),
            Vertex(Vec3(0.1, 0.1, 0.0), Vec2(+1, +2/4)),
            Vertex(Vec3(0 , 0.3, 0.0), Vec2(+1/2, +4/4)),
        ])
        

    @metsig(Element.__init__)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.controller = ShipController()
        self._last_shot_time = time.time()

    def _get_bounding_box_vertices(self) -> Rect2:
        return np.array([
            [-0.1, -0.1, 0], 
            [+0.1, -0.1, 0],
            [+0.1, +0.3, 0],
            [-0.1, +0.3, 0],
        ])

    def _physics_update(self, delta_time: float):
        self.shoot()    
        print(f'BBOX = {self.get_bounding_box()}')

        self.controller.process_input()
        if self.controller.input_movement != 0:
            self.move_forward(self.controller.input_movement)
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
        return False

    def shoot(self):
        curr_time = time.time()

        if (curr_time - self._last_shot_time) < SHOOTING_COOLDOWN:
            return

        if not IS.is_pressed('space'):
            return

        self._last_shot_time = curr_time

        Projectile.create_from(self)