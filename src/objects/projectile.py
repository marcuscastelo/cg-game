from copy import copy, deepcopy
from math import cos, sin
from dataclasses import dataclass
import math
from typing import TYPE_CHECKING

from utils.geometry import Rect, Rect2, Vec2, Vec3
from utils.logger import LOGGER
from objects.element import Element
import numpy as np

from utils.sig import metsig

from OpenGL import GL as gl

from transformation_matrix import Transform

if TYPE_CHECKING:
    from objects.ship import Ship

@dataclass
class ProjectileSpecs:
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
    @metsig(Element.__init__)
    def __init__(self, *args, specs: ProjectileSpecs = ProjectileSpecs(), **kwargs):
        self.specs = specs
        self._render_primitive = gl.GL_LINES
        super().__init__(*args, **kwargs)
        self.is_particle = True
        self.speed = self.specs.initial_speed

    def _init_vertices(self):
        self._render_primitive = gl.GL_LINES

        # Vertices are defined to take the whole screen (vertically), so that transformations are easier
        self._vertices = [
            *(0.0,  -1.0,    0.0),
            *(0.0,  1.0,   0.0),
        ]
        self.transform.scale.y = self.specs.length

    def _render(self):
        gl.glLineWidth(self.specs.width)
        return super()._render()

    @classmethod
    def create_from(cls, ship: 'Ship') -> 'Projectile':
        relavite_weapon_distance = Vec3(-sin(ship.angle), cos(ship.angle), 0) * ship.ship_len
        projectile_pos = ship.transform.translation.xyz + relavite_weapon_distance 
        
        obj = cls(ship.world, Transform(translation=projectile_pos, rotation=Vec3(0, 0, ship.angle)))
        obj.is_particle = False
        return obj

    def too_small(self):
        return self.transform.scale.y < 0.01


    
    def _physics_update(self):
        if self.destroyed:
            LOGGER.log_warning(f"Trying to update destroyed projectile {self}")
            return

        self.move()
        self.speed = max(self.speed + self.speed * self.specs.acceleration, 0)

        self.transform.scale.y *= (1 - self.specs.decay_rate)

        screen = Rect2(-1, -1, 1, 1)
        outside_screen = not screen.contains(self.transform.translation.xy)

        if outside_screen or self.too_small():
            self.destroy()

    def destroy(self):
        # if not self.destroyed and not self.too_small() and not self.is_particle:
        #     # impact_xyz = self.transform.translation.xyz
        #     # number_of_minibullets = 10
        #     # angle_step = 2 * math.pi / number_of_minibullets
        #     # mini_bullets = [
        #     #     Projectile(self.world, Transform(translation=impact_xyz + Vec3(0, 0, 0.1), rotation=Vec3(0, 0, angle_step * i))) for i in range(number_of_minibullets)
        #     # ]

        #     # for bullet in mini_bullets:
        #     #     bullet.transform.scale.y = 0.1

        return super().destroy()

    
