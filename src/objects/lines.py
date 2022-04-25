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
    from world import World

@dataclass
class Lines(Element):
    def __init__(self, world: 'World', points: list[Vec3], initial_transform: Transform = Transform(), **kwargs):
        self.points = points
        super().__init__(world, initial_transform, **kwargs)

    def _init_vertices(self):
        self._render_primitive = gl.GL_LINES

        vertices = [*self.points[0]]
        for i in range(1, len(self.points)):
            vertices += [*self.points[i]]
            vertices += [*self.points[i]]

        vertices.pop()

        print(f'Lines vertices: {vertices}')
        self._vertices = np.array(vertices, dtype=np.float32)
        print(f'Lines _vertices: {self._vertices}')

    def _render(self):
        gl.glLineWidth(0.5)
        return super()._render()

    def _physics_update(self, _):
        pass