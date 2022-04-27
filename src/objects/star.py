from dataclasses import dataclass
from OpenGL import GL as gl
import numpy as np
from numpy import log

from utils.geometry import Vec2, Vec3
from utils.sig import metsig

from objects.element import Element, Vertex, VertexSpecification


@dataclass(init=False)
class Stars(Element):
    star_size: float = 0.02
    rotation_speed: float = 0.1

    def _create_vertex_buffer(self) -> VertexSpecification:
        return VertexSpecification([
            Vertex(Vec3(0, self.star_size, 0.0)),
            Vertex(Vec3(-self.star_size*0.58, -self.star_size*0.81, 0.0)),
            Vertex(Vec3(self.star_size*0.36, -self.star_size*0.12, 0.0)),

            Vertex(Vec3(-self.star_size*0.58, -self.star_size*0.81, 0.0)),
            Vertex(Vec3(self.star_size*0.95, self.star_size*0.31, 0.0)),
            Vertex(Vec3(-self.star_size*0.22, self.star_size*0.31, 0.0)),

            Vertex(Vec3(self.star_size*0.58, -self.star_size*0.81, 0.0)),
            Vertex(Vec3(self.star_size*0.22, self.star_size*0.31, 0.0)),
            Vertex(Vec3(-self.star_size*0.95, self.star_size*0.31, 0.0)),
        ])

    @metsig(Element.__init__)
    def __init__(self, *args, **kwargs):
        self._render_primitive = gl.GL_TRIANGLE_STRIP
        super().__init__(*args, **kwargs)

    def _physics_update(self, delta_time: float):
        self.transform.translation.xy += Vec2( 0.01, -(log((self.transform.translation.x+2)))/200 )
        self.rotate(0.1)

    def _on_outside_screen(self, _):
        self.transform.translation.xy = Vec2(-1, np.random.random()*(2)-1)

    def _get_bounding_box_vertices(self) -> np.ndarray:
        return np.array([
            [-self.star_size*0.95, -self.star_size*0.81, 0.0],
            [ self.star_size*0.95,  self.star_size*0.81, 0.0],
            [-self.star_size*0.95,  self.star_size*0.81, 0.0],
            [ self.star_size*0.95, -self.star_size*0.81, 0.0],
        ])