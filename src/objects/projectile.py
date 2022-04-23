import math
from typing import TYPE_CHECKING
from objects.element import Element

from utils.sig import metsig

from OpenGL import GL as gl

if TYPE_CHECKING:
    from objects.ship import Ship

PROJECTILE_WIDTH = 0.05

class Projectile(Element):
    @metsig(Element.__init__)
    def __init__(self, *args, **kwargs):
        self._render_primitive = gl.GL_LINES
        super().__init__(*args, **kwargs)

    def _init_vertices(self):
        self._vertices = [
            *(0, 0),
            *(0, 0.05),
        ]

    def render(self):
        gl.glLineWidth(PROJECTILE_WIDTH)
        return super().render()

    @classmethod
    def create_from(cls, ship: 'Ship') -> 'Projectile':
        obj = cls((ship.x, ship.y, ship.z))
        obj.angle = ship.angle
        return obj

    def _physic_update(self):
        self.move(0.1)
