from dataclasses import dataclass
import math
import time
from glm import clamp
from OpenGL import GL as gl

from utils.geometry import Rect2, Vec2, Vec3, VecN
from utils.logger import LOGGER
from utils.sig import metsig
from constants import SCREEN_RECT
from gl_abstractions.texture import Texture2D
from objects.element import Element, ElementSpecification, ShapeRenderer, ShapeSpec
from objects._2d.garbage import Garbage
from objects._2d.projectile import Projectile

from input.input_system import INPUT_SYSTEM as IS

import numpy as np
from gl_abstractions.shader import ShaderDB

from transform import Transform

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
    input_movement: float = 0 # Translation movement (in input terms, not actual translation)
    input_rotation: float = 0 # Rotation movement (in input terms, not actual rotation)
    input_squeeze: float = 1 # Squeeze movement (in input terms, not actual squeeze)

    enabled = False
    keybinds = {
        "forward": "w",
        "backward": "s",
        "left": "a",
        "right": "d",
        "squeeze": "x",
    }

    def enable(self):
        '''Enable the controller. Now the user can control the ship.'''
        self.enabled = True
    def disable(self):
        '''Disable the controller. Now the user can't control the ship.'''
        self.enabled = False

    def process_input(self):
        '''Process the input. This is called every frame to update the movement of the ship.'''
        # Multipliers controlled by 'shift' and 'control' keys (make faster or slower)
        trans_multiplier = 1
        rot_multiplier = 1

        # Only process input if enabled
        if not self.enabled:
            return
        
        ### Actual keybind input processing ###

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

        #### #### #### ####

@dataclass(init=False)
class Ship(Element):
    '''
    Ship is the user controlled element.
    It represents the player in the game.
    The player can move around the screen and shoot.
    The keybinds are stored in the ShipController class.
    '''

    _rotation_intensity = 0 # Used for smoothing the rotation movement (like an acceleration)

    @metsig(Element.__init__)
    def __init__(self, *args, **kwargs):

        # Define color pallete to the object Star
        darker_silver: Vec3 = Vec3(110, 110, 110) / 255
        dark_silver: Vec3 = Vec3(121, 121, 121) / 255
        silver: Vec3 = Vec3(169,169,169) / 255
        light_silver: Vec3 = Vec3(192,192,192) / 255
        lighter_silver: Vec3 = Vec3(211,211,211) / 255
        
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
                        [*(-0.075, -0.075, 0.0), *(light_silver)],
                        [*( 0.075, -0.075, 0.0), *(dark_silver)],
                        [*(-0.075,  0.075, 0.0), *(silver)],
                            
                        [*( 0.075, -0.075, 0.0), *(dark_silver)],
                        [*( 0.075,  0.075, 0.0), *(dark_silver)],
                        [*(-0.075,  0.075, 0.0), *(silver)],
                        
                        # Ship's point
                        [*(-0.075,  0.075, 0.0), *(light_silver)],
                        [*( 0.075,  0.075, 0.0), *(darker_silver)],
                        [*( 0.0,  0.225, 0.0), *(silver)],
                        
                        # Ship's propulsors
                        [*(0.035, -0.075, 0.0), *(dark_silver)],
                        [*(0.055, -0.075, 0.0), *(dark_silver)],
                        [*(0.055, -0.09, 0.0), *(dark_silver)],
                        [*(0.035, -0.075, 0.0), *(dark_silver)],
                        [*(0.035, -0.09, 0.0), *(dark_silver)],
                        [*(0.055, -0.09, 0.0), *(dark_silver)],
                        
                        [*(-0.035, -0.075, 0.0), *(silver)],
                        [*(-0.055, -0.075, 0.0), *(silver)],
                        [*(-0.055, -0.09, 0.0), *(silver)],
                        [*(-0.035, -0.075, 0.0), *(silver)],
                        [*(-0.035, -0.09, 0.0), *(silver)],
                        [*(-0.055, -0.09, 0.0), *(silver)],
                    ], dtype=np.float32),
                    shader=ShaderDB.get_instance().get_shader('colored'), # Shader uses colors defined in the vertices
                ),

                ShapeSpec(
                    vertices=np.array([
                        #Wings
                        [*(0.075, 0.0, 0.0), *(silver)],
                        [*(0.075, -0.01, 0.0), *(silver)],
                        [*(0.115, -0.015, 0.0), *(dark_silver)],

                        [*(0.075, 0.0, 0.0), *(dark_silver)],
                        [*(0.115, -0.015, 0.0), *(darker_silver)],
                        [*(0.13, 0.0, 0.0), *(darker_silver)],

                        [*(0.13, -0.04, 0.0), *(darker_silver)],
                        [*(0.13, 0.0, 0.0), *(darker_silver)],
                        [*(0.115, -0.015, 0.0), *(darker_silver)],

                        [*(-0.075, 0.0, 0.0), *(silver)],
                        [*(-0.075, -0.01, 0.0), *(silver)],
                        [*(-0.115, -0.015, 0.0), *(silver)],

                        [*(-0.075, 0.0, 0.0), *(light_silver)],
                        [*(-0.115, -0.015, 0.0), *(lighter_silver)],
                        [*(-0.13, 0.0, 0.0), *(light_silver)],

                        [*(-0.13, -0.04, 0.0), *(lighter_silver)],
                        [*(-0.13, 0.0, 0.0), *(lighter_silver)],
                        [*(-0.115, -0.015, 0.0), *(lighter_silver)],
                    ], dtype = np.float32),
                    shader=ShaderDB.get_instance().get_shader('colored'),
                    
                ),
            ]
        )
        super().__init__(*args, **kwargs)
        self.controller = ShipController()
        self._last_shot_time = time.time()

    def _generate_bounding_box_2d_vertices(self) -> np.ndarray:
        '''Overrides the default bounding box generation'''
        return np.array([
            [-0.075, -0.09 , 0.0],
            [+0.075, -0.09 , 0.0],
            [+0.075, +0.155, 0.0],
            [-0.075, +0.155, 0.0],
        ])

    def _physics_shoot(self, delta_time: float):
        '''Check if user wants to shoot and shoot if so'''
        if IS.is_pressed('space'):
            self.shoot()    

    def _physics_movement(self, delta_time: float):
        '''Read user input from ShipController and move the ship accordingly'''

        self.controller.process_input()
        
        if self.controller.input_movement != 0:
            # Translation occurs in the direction of the current angle we are facing
            dx = np.cos(self.transform.rotation.z + math.radians(90)) * 1 * self.speed
            dy = np.sin(self.transform.rotation.z + math.radians(90)) * 1 * self.speed
            self.transform.translation.xy += Vec2(dx, dy)
        if self.controller.input_rotation != 0:
            # Rotation occurs in a smoothed fashion (gradually accelerate to the target angular speed)
            ROT_ACCEL = 3.5

            if self._rotation_intensity * self.controller.input_rotation < 0:
                self._rotation_intensity = 0 # Turning direction changed

            self._rotation_intensity += self.controller.input_rotation * delta_time * ROT_ACCEL

            inp_abs = abs(self.controller.input_rotation)
            min_rot = -inp_abs
            max_rot = inp_abs
            self._rotation_intensity = clamp(self._rotation_intensity, min_rot, max_rot)

            self.transform.rotation.z += self._rotation_intensity
        else:
            # Imediatelly stop rotation
            self._rotation_intensity = 0
            pass

        SHRINK_RATE = 5
        REGROWTH_RATE = SHRINK_RATE
        if self.controller.input_squeeze != 0:
            # Shrink the ship if key is pressed
            MIN_SCALE = 0.8

            t = self.transform
            t.scale *= (1 - self.controller.input_squeeze*(1-MIN_SCALE) * SHRINK_RATE * delta_time)


            if t.scale.x < MIN_SCALE:
                t.scale = Vec3(MIN_SCALE, MIN_SCALE, MIN_SCALE)
        else:
            # Regrow the ship if key is not pressed
            t = self.transform
            t.scale *= (1 + REGROWTH_RATE * delta_time)
            if t.scale.x > 1:
                t.scale = Vec3(1, 1, 1)

    def _die_if_enemy_shot(self):
        '''Check if the ship was shot by an enemy and die if so'''
        from objects._2d.enemy import Enemy
        if self._dying:
            return

        # for obj in ( element for element in self.world.elements if isinstance(element, (Projectile, Enemy ) )):
        #     if (not isinstance(obj, Projectile) or obj.is_enemy) and self.get_bounding_box_2d().contains(obj.transform.translation.xy):
        #         LOGGER.log_debug('Ship hit by enemy projectile', 'Ship')
        #         obj.destroy()
        #         self.die()
        #         return

    def _physics_update(self, delta_time: float):
        '''Overrides the default physics update to add custom physics'''
        if self._dying:
            # Add to death animation a rotation effect
            self.rotate(math.radians(90) * delta_time)
        else:
            # Only update physics if the ship is not dying (prevents us from shooting or moving while dying)
            self._physics_shoot(delta_time)
            self._physics_movement(delta_time)
            self._die_if_enemy_shot()
        
        # bbox = self.get_bounding_box_2d()

        # # Collect garbage near the ship
        # for garbage in (element for element in self.world.elements if isinstance(element, Garbage)):
        #     if bbox.intersects(garbage.get_bounding_box_2d()):
        #         garbage.destroy()
        
        # # Ship is out of bounds if any of the corners are outside the screen (diferent from other elements, in which all the vertices must be outside the screen)
        # for points in [ bbox.top_left, bbox.top_right, bbox.bottom_left, bbox.bottom_right ]:
        #     if not SCREEN_RECT.contains(points):
        #         self._on_outside_screen()


        return super()._physics_update(delta_time)

    def _on_outside_screen(self):
        '''
        Overrides the default behaviour of the ship when it goes outside the screen
        The default behaviour is to destroy it
        But we want to keep it alive and in the screen
        '''

        # Apply a pseudo-force to the ship to keep it inside the screen
        min_x, min_y, max_x, max_y = self.get_bounding_box_2d()
        if min_x < -1:
            self.transform.translation.xy += -Vec2(min_x + 1, 0)/16
        if max_x > 1:
            self.transform.translation.xy += -Vec2(max_x - 1, 0)/16
        if min_y < -1:
            self.transform.translation.xy += -Vec2(0, min_y + 1)/16
        if max_y > 1:
            self.transform.translation.xy += -Vec2(0, max_y - 1)/16
        

    def shoot(self):
        '''
        Allow the ship to shoot a projectile by pressing the keybind
        '''
        curr_time = time.time()

        if (curr_time - self._last_shot_time) < SHOOTING_COOLDOWN:
            return

        self._last_shot_time = curr_time

        Projectile.create_from_ship(self)