from math import cos, sin
from dataclasses import dataclass
import math
from typing import TYPE_CHECKING

from utils.geometry import Rect2, Vec2, Vec3
from utils.logger import LOGGER
from objects.element import Element, ElementSpecification, ShapeSpec

from OpenGL import GL as gl

from transformation_matrix import Transform

import numpy as np

if TYPE_CHECKING:
    from objects.ship import Ship
    from world import World

@dataclass
class ProjectileSpecs(ElementSpecification):
    """
    This class is used to store the movement of the ship.
    User input is stored in this class. (in the current frame)
    """
    initial_speed: float = 0.06
    acceleration: float = +0.005
    decay_rate: float = 0.1
    length: float = 0.16
    width: float = 0.5
    color: Vec3 = Vec3(1, 0, 0)

@dataclass
class Projectile(Element):
    def __init__(self, world: 'World', specs: ProjectileSpecs, *args, **kwargs):
        self.live_time = 0
        self.projectile_specs = specs
        
        # TODO: avoid scale overwriting somehow (if user already set scale before)
        specs.initial_transform.scale.y = specs.length
        specs.shape_specs = [
            ShapeSpec(vertices=np.array([
                *(0.0,  -1.0,   0.0),
                *(0.0,  +1.0,   0.0),
            ], dtype=np.float32),
            render_mode=gl.GL_LINES,
            )
        ]

        super().__init__(world, specs, *args, **kwargs)

        self.is_particle = True # TODO: remove this and create a proper particle class
        self.speed = self.projectile_specs.initial_speed

    def _get_bounding_box_vertices(self) -> np.ndarray:
        return np.array([
            [-0.01, -1, 0],
            [+0.01, +1, 0],
        ])

    def _render(self):
        gl.glLineWidth(self.projectile_specs.width)
        return super()._render()

    @classmethod
    def create_from_ship(cls, ship: 'Ship') -> 'Projectile':
        relatite_weapon_distance = Vec3(-sin(ship.angle), cos(ship.angle), 0) * ship.ship_len
        projectile_pos = ship.transform.translation.xyz + relatite_weapon_distance 
        
        obj = cls(
            world = ship.world,
            specs = ProjectileSpecs(
                initial_transform=Transform(
                    translation=projectile_pos, 
                    rotation=Vec3(0, 0, ship.angle)),
            )
        )

        obj.is_particle = False
        return obj

    def too_small(self):
        return self.transform.scale.y < 0.01
    
    def _physics_update(self, delta_time: float):
        self.live_time += delta_time
        if self.destroyed:
            LOGGER.log_error(f"Trying to update destroyed projectile {self}")
            return

        self.move_forward()
        self.speed = max(self.speed + self.speed * self.projectile_specs.acceleration, 0)

        self.transform.scale.y *= (1 - self.projectile_specs.decay_rate)

        screen = Rect2(-1, -1, 1, 1)
        outside_screen = not screen.contains(self.transform.translation.xy)

        if outside_screen or self.too_small():
            if not self.destroyed:
                self.destroy()

        return super()._physics_update(delta_time)

    def destroy(self):
        # if not self.destroyed and not self.too_small() and not self.is_particle:
        #     impact_xyz = self.transform.translation.xyz
        #     TIME_TO_TRAVEL_SCREEN = 1 # seconds
        #     MAX_PARTICLES = 50
        #     particle_lifetime_completion = min(1, self.live_time / TIME_TO_TRAVEL_SCREEN)

        #     number_of_minibullets = int(math.ceil(MAX_PARTICLES * particle_lifetime_completion)) + 3
        #     start_angle = self.transform.rotation.z
        #     angle_step = 2 * math.pi / number_of_minibullets

        #     initial_speed=self.projectile_specs.initial_speed * 0.5,
        #     decay_rate=self.projectile_specs.decay_rate * 4
            
        #     mini_bullets = [
        #         Projectile(
        #             self.world, 
        #             specs=ProjectileSpecs(
        #                 initial_speed=initial_speed,
        #                 decay_rate=decay_rate,
        #                 initial_transform=Transform(
        #                     translation=impact_xyz + Vec3(0, 0, 0.1), 
        #                     rotation=Vec3(0, 0, start_angle + math.pi/2 + angle_step/2 * i)
        #                 )
        #             )
        #         ) for i in range(number_of_minibullets)
        #     ]

        #     for bullet in mini_bullets:
        #         bullet.transform.scale.y = 0.1

        return super().destroy()

    
