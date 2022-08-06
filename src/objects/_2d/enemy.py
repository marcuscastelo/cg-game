import math
import random
from glm import clamp
from utils.geometry import Rect2, Vec2, Vec3
from utils.logger import LOGGER
from utils.sig import metsig
from objects.element import Element, ElementSpecification, ShapeSpec
from objects._2d.projectile import Projectile, ProjectileSpecs

import numpy as np

from gl_abstractions.shader import ShaderDB
from objects._2d.ship import Ship

from transform import Transform

MAX_SPEED = 0.4
ACCEL = 0.8

class Enemy(Element):
    '''
    Enemy class, responsible to try to destroy the ship by shooting at it.
    Must all be destroyed so the player can win.
    Represents an enemy ship in the game.
    The enemy ship is made of 4 triangles, each one representing a side of the ship.
    It checks every physics update if it collides with any projectile. If it does, it dies. and the projectile is destroyed.
    It moves in a straight, back and forth motion. It also rotates around its center to aim at the player.
    It shoots a projectile randomly (with a probability of 0.01) every second.
    '''
    @metsig(Element.__init__)
    def __init__(self, *args, **kwargs):

        # Define color pallete to the object Star
        orange: Vec3 = Vec3(255,100,100) / 255
        light_red: Vec3 = Vec3(219,48,86) / 255
        red: Vec3 = Vec3(255,0,0) / 255
        dark_red: Vec3 = Vec3(133,29,65) / 255
        # TODO: find a better way to do this (kwargs)
        kwargs['specs'] = ElementSpecification(
            initial_transform=Transform(
                translation=Vec3(0, 0, 0),
                rotation=Vec3(0, 0, math.pi),
                scale=Vec3(1, 1, 1),
            ),
            shape_specs=[
                ShapeSpec(vertices=np.array([
                    #Left
                    [*(-0.075, -0.075, 0.0), *(orange)],
                    [*(-0.075, 0.0, 0.0), *(orange)],
                    [*(0.0, -0.05, 0.0), *(red)],

                    #Right
                    [*(0.0, -0.05, 0.0), *(red)],
                    [*(0.075, 0.0, 0.0), *(dark_red)],
                    [*(0.075, -0.075, 0.0), *(dark_red)],

                    #Center
                    [*(-0.075, 0.0, 0.0), *(orange)],
                    [*(0.075, 0.0, 0.0), *(dark_red)],
                    [*(0.0, -0.05, 0.0), *(red)],

                    #Front
                    [*(-0.075, 0.0, 0.0), *(orange)],
                    [*(0.075, 0.0, 0.0), *(dark_red)],
                    [*(0.0, +0.055, 0.0), *(light_red)],
                ], dtype=np.float32),
                shader=ShaderDB.get_instance().get_shader('colored'),
                name='Enemy Full',
                ),
            ]
        )


        super().__init__(*args, **kwargs)
        # TODO: remove old 2D logic
        self.speed = 1 # [-MAX_SPEED, MAX_SPEED]
        self._accel_dir = 1 # {-1, 1}
        pass

    def _generate_bounding_box_2d_vertices(self) -> np.ndarray:
        '''Overrides the bounding box generation of the Element class'''
        return np.array([
            [-0.075, -0.075, 0],
            [+0.075, -0.075, 0],
            [+0.075, +0.075, 0],
            [-0.075, -0.075, 0],
        ])

    def _physics_update(self, delta_time: float):
        '''Overrides the physics update of the Element class'''
        # bbox = self.get_bounding_box_2d()
        projectiles = ( element for element in self.world.elements if isinstance(element, Projectile) )

        ship = ( element for element in self.world.elements if isinstance(element, Ship) )
        ship = next(ship, None)
        if ship is None:
            self.rotate(0.01)
        else:
            self.transform.rotation.z = math.atan2(-ship.transform.translation.y + self.transform.translation.y, -ship.transform.translation.x + self.transform.translation.x) + math.pi / 2
            if random.random() > 0.99:
                # Projectile(self.world, ProjectileSpecs())
                Projectile.create_from_ship(self, specs=ProjectileSpecs(initial_speed=0.025, decay_rate=0.03)).is_enemy = True

        for projectile in projectiles:
            if projectile.is_particle:
                continue
            
            # if not bbox.contains(projectile.transform.translation.xy):
            #     continue

            # LOGGER.log_debug(f'Enemy(id={id(self)}) hit by projectile(id={id(projectile)})')
            # if not projectile.is_enemy:
            #     self.speed = 0
            #     self._accel_dir = 0
            #     self.die()

            # projectile.destroy()


        # Move

        self.speed = clamp(self.speed + self._accel_dir * ACCEL * delta_time, -MAX_SPEED, MAX_SPEED)
        if abs(self.speed) >= MAX_SPEED:
            self._accel_dir *= -1

        self.transform.translation.xy += Vec2(self.speed, 0) * delta_time

        return super()._physics_update(delta_time)