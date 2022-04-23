from math import cos, sin
from dataclasses import dataclass
import math
from typing import TYPE_CHECKING
from objects.element import Element
import numpy as np

from utils.sig import metsig

from OpenGL import GL as gl

if TYPE_CHECKING:
    from objects.ship import Ship

PROJECTILE_WIDTH = 0.05

@dataclass
class Projectile(Element):
    @metsig(Element.__init__)
    def __init__(self, *args, **kwargs):
        self._render_primitive = gl.GL_LINES
        super().__init__(*args, **kwargs)

    def _init_vertices(self):
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
        xyz = np.array((ship.x, ship.y, ship.z), dtype=np.float32)
        
        weapon_dx = -ship.ship_len * sin(ship.angle)
        weapon_dy = ship.ship_len * cos(ship.angle)

        xyz += np.array((weapon_dx, weapon_dy, 0), dtype=np.float32)

        obj = cls((xyz[0], xyz[1], xyz[2]))
        obj.angle = ship.angle
        return obj

    def _physics_update(self):
        self.move(0.03)
        print(f'Projectile at {self.x}, {self.y}')
        if self.x < -1 or self.x > 1 or self.y < -1 or self.y > 1:
            self.destroy()
        # pass

    
