from dataclasses import dataclass
import math
import time
from glm import clamp
from OpenGL import GL as gl

from utils.geometry import Rect2, Vec2, Vec3, VecN
from utils.logger import LOGGER
from utils.sig import metsig
from gl_abstractions.texture import Texture2D
from objects.element import Element, ElementSpecification, ShapeRenderer, ShapeSpec
from objects.garbage import Garbage
from objects.projectile import Projectile

from input.input_system import INPUT_SYSTEM as IS

import numpy as np
from shader import ShaderDB

from transformation_matrix import Transform

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

    # def DEPRECATED_USE_SPECS_IN_CONSTRUCTOR(self) -> VertexSpecification:
    #     return VertexSpecification([
    #         Vertex(Vec3(-0.1, -0.1, 0.0), Vec2(0, 0)),
    #         Vertex(Vec3(0.1, -0.1, 0.0), Vec2(1, 0)),
    #         Vertex(Vec3(-0.1, 0.1, 0.0), Vec2(0, +2/4)),
            
    #         Vertex(Vec3(0.1, -0.1, 0.0), Vec2(+1, 0)),
    #         Vertex(Vec3(0.1, 0.1, 0.0), Vec2(+1, +2/4)),
    #         Vertex(Vec3(-0.1, 0.1, 0.0), Vec2(0, +2/4)),

    #         Vertex(Vec3(-0.1, 0.1, 0.0), Vec2(0, +2/4)),
    #         Vertex(Vec3(0.1, 0.1, 0.0), Vec2(+1, +2/4)),
    #         Vertex(Vec3(0 , 0.3, 0.0), Vec2(+1/2, +4/4)),
    #     ])
        

    @metsig(Element.__init__)
    def __init__(self, *args, **kwargs):

        ship_front_color: Vec3 = Vec3(211,211,211) / 255
        ship_body_color: Vec3 = Vec3(169,169,169) / 255
        ship_wing_color: Vec3 = Vec3(192,192,192) / 255
        ship_propulsor_color: Vec3 = Vec3(128,128,128) / 255
        
        # TODO: find a better way to do this (kwargs)
        kwargs['specs'] = ElementSpecification(
            initial_transform=Transform(
                translation=Vec3(0, 0, 0),
                rotation=Vec3(0, 0, 0),
                scale=Vec3(1, 1, 1),
            ),
            shape_specs=[
                ShapeSpec( 
                    vertices=np.array([
                        # Ship's body
                        *(-0.075, -0.075, 0.0), *(ship_body_color),
                        *( 0.075, -0.075, 0.0), *(ship_body_color),
                        *(-0.075,  0.075, 0.0), *(ship_body_color),

                        *( 0.075, -0.075, 0.0), *(ship_body_color),
                        *( 0.075,  0.075, 0.0), *(ship_body_color),
                        *(-0.075,  0.075, 0.0), *(ship_body_color),
                        
                        # Ship's point
                        *(-0.075,  0.075, 0.0), *(ship_front_color),
                        *( 0.075,  0.075, 0.0), *(ship_front_color),
                        *( 0.0,  0.225, 0.0), *(ship_front_color),

                        # Ship's propulsors
                        *(0.035, -0.075, 0.0), *(ship_propulsor_color),
                        *(0.055, -0.075, 0.0), *(ship_propulsor_color),
                        *(0.055, -0.09, 0.0), *(ship_propulsor_color),
                        *(0.035, -0.075, 0.0), *(ship_propulsor_color),
                        *(0.035, -0.09, 0.0), *(ship_propulsor_color),
                        *(0.055, -0.09, 0.0), *(ship_propulsor_color),

                        *(-0.035, -0.075, 0.0), *(ship_propulsor_color),
                        *(-0.055, -0.075, 0.0), *(ship_propulsor_color),
                        *(-0.055, -0.09, 0.0), *(ship_propulsor_color),
                        *(-0.035, -0.075, 0.0), *(ship_propulsor_color),
                        *(-0.035, -0.09, 0.0), *(ship_propulsor_color),
                        *(-0.055, -0.09, 0.0), *(ship_propulsor_color),
                    ], dtype=np.float32),
                    shader=ShaderDB.get_instance().get_shader('colored'), # Shader uses colors defined in the vertices
                ),

                ShapeSpec(
                    vertices=np.array([
                        #Wings
                        *(0.075, 0.0, 0.0), *(ship_wing_color),
                        *(0.075, -0.01, 0.0), *(ship_wing_color),
                        *(0.115, -0.015, 0.0), *(ship_wing_color),

                        *(0.075, 0.0, 0.0), *(ship_wing_color),
                        *(0.115, -0.015, 0.0), *(ship_wing_color),
                        *(0.13, 0.0, 0.0), *(ship_wing_color),

                        *(0.13, -0.04, 0.0), *(ship_wing_color),
                        *(0.13, 0.0, 0.0), *(ship_wing_color),
                        *(0.115, -0.015, 0.0), *(ship_wing_color),

                        *(-0.075, 0.0, 0.0), *(ship_wing_color),
                        *(-0.075, -0.01, 0.0), *(ship_wing_color),
                        *(-0.115, -0.015, 0.0), *(ship_wing_color),

                        *(-0.075, 0.0, 0.0), *(ship_wing_color),
                        *(-0.115, -0.015, 0.0), *(ship_wing_color),
                        *(-0.13, 0.0, 0.0), *(ship_wing_color),

                        *(-0.13, -0.04, 0.0), *(ship_wing_color),
                        *(-0.13, 0.0, 0.0), *(ship_wing_color),
                        *(-0.115, -0.015, 0.0), *(ship_wing_color),
                    ], dtype = np.float32),
                    shader=ShaderDB.get_instance().get_shader('colored'),
                    
                ),

                ShapeSpec( 
                    vertices=np.array([
                        # Ship's body
                        *(-0.075, -0.075, 0.0), *(0.0, 0.0),
                        *( 0.075, -0.075, 0.0), *(1.0, 0.0),
                        *(-0.075,  0.075, 0.0), *(0.0, 1.0),

                        *( 0.075, -0.075, 0.0), *(1.0, 0.0),
                        *( 0.075,  0.075, 0.0), *(1.0, 1.0),
                        *(-0.075,  0.075, 0.0), *(0.0, 1.0),
                    ], dtype=np.float32),
                    shader=ShaderDB.get_instance().get_shader('textured'), # Shader uses colors defined in the vertices
                    name='ship_body_textured',
                    texture=Texture2D.from_image_path('textures/enemy_texture.jpg'),
                ),


            ]
        )
        super().__init__(*args, **kwargs)
        self.controller = ShipController()
        self._last_shot_time = time.time()

        bbox = self.get_bounding_box()
        min_x, min_y, max_x, max_y = bbox

    def _get_bounding_box_vertices(self) -> Rect2:
        return np.array([
            [-0.075, -0.09 , 0.0],
            [+0.075, -0.09 , 0.0],
            [+0.075, +0.225, 0.0],
            [-0.075, +0.225, 0.0],
        ])

    def _physics_shoot(self, delta_time: float):
        if IS.is_pressed('space'):
            self.shoot()    

    def _physics_movement(self, delta_time: float):
        self.controller.process_input()
        if self.controller.input_movement != 0:
            LOGGER.log_debug('Trying to move', 'Ship')
            self.move_forward(self.controller.input_movement)
            LOGGER.log_debug(f'Translation: {self.transform.translation}', 'Ship')
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

    def _physics_update(self, delta_time: float):
        self._physics_shoot(delta_time)
        self._physics_movement(delta_time)

        for garbage in (element for element in self.world.elements if isinstance(element, Garbage)):
            if self.get_bounding_box().intersects(garbage.get_bounding_box()):
                garbage.destroy()
            

        return super()._physics_update(delta_time)

    def shoot(self):
        curr_time = time.time()

        if (curr_time - self._last_shot_time) < SHOOTING_COOLDOWN:
            return

        self._last_shot_time = curr_time

        Projectile.create_from_ship(self)