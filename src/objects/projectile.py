from copy import copy, deepcopy
from math import cos, sin
from dataclasses import dataclass
import math
from typing import TYPE_CHECKING

from utils.geometry import Rect, Vec2, Vec3
from utils.logger import LOGGER
from objects.element import Element
import numpy as np

from utils.sig import metsig

from OpenGL import GL as gl

from transformation_matrix import Transform
from world import WORLD

if TYPE_CHECKING:
    from objects.ship import Ship

PROJECTILE_WIDTH = 0.5
PROJECTILE_SPEED = 0.1

@dataclass
class Projectile(Element):
    @metsig(Element.__init__)
    def __init__(self, *args, **kwargs):
        self._render_primitive = gl.GL_LINES
        super().__init__(*args, **kwargs)
        self.is_particle = True

    def _init_vertices(self):
        self._render_primitive = gl.GL_LINES
        self._vertices = [
            *(0.0,  0.0,    0.0),
            *(0.0,  0.15,   0.0),
            # *(0.15, 0.15,   0.0),
        ]

    def _render(self):
        gl.glLineWidth(PROJECTILE_WIDTH)
        return super()._render()

    @classmethod
    def create_from(cls, ship: 'Ship') -> 'Projectile':
        relavite_weapon_distance = Vec3(-sin(ship.angle), cos(ship.angle), 0) * ship.ship_len
        projectile_pos = ship.transform.translation.xyz + relavite_weapon_distance 
        
        obj = cls(Transform(translation=projectile_pos, rotation=Vec3(0, 0, ship.angle)))
        obj.is_particle = False
        return obj

    def too_small(self):
        return self.transform.scale.y < 0.01

    def _physics_update(self):
        if self.destroyed:
            LOGGER.log_warning(f"Trying to update destroyed projectile {self}")
            return
            
        self.move(PROJECTILE_SPEED)
        self.transform.scale.y *= 0.85

        inside_screen = self.transform.translation.xy in Rect(-1, -1, 2, 2)

        if not inside_screen or self.too_small():
            self.destroy()

    def destroy(self):
        if not self.destroyed and not self.too_small():
            impact_xyz = self.transform.translation.xyz
            number_of_minibullets = 10
            angle_step = 2 * math.pi / number_of_minibullets
            mini_bullets = [
                Projectile(Transform(translation=impact_xyz + Vec3(0, 0, 0.1), rotation=Vec3(0, 0, angle_step * i))) for i in range(number_of_minibullets)
            ]

            for bullet in mini_bullets:
                bullet.transform.scale.y = 0.1
                bullet.destroy = super().destroy
                WORLD.add_element(bullet)

        return super().destroy()

    
