from dataclasses import dataclass
from OpenGL import GL as gl
import numpy as np
from numpy import log

from utils.geometry import Vec2, Vec3
from utils.sig import metsig

from objects.element import Element, ElementSpecification, ShapeSpec
from gl_abstractions.shader import ShaderDB
from transform import Transform


@dataclass(init=False)
class Star(Element):
    star_size: float = 0.02
    rotation_speed: float = 0.1

    @metsig(Element.__init__)
    def __init__(self, *args, **kwargs):

        Star_color: Vec3 = Vec3(255, 255, 0.0) / 255 * 0.3 # Make darker
        kwargs['specs'] = ElementSpecification(
            initial_transform=Transform(
                translation=Vec3(0, 0, 0),
                rotation=Vec3(0, 0, 0),
                scale=Vec3(self.star_size, self.star_size, 1) * 3,
            ), # TODO: allow world to set this
            shape_specs=[
                ShapeSpec(
                    vertices=np.array([
                        [*( 0.00,  1.00, +0.0), *(Star_color)],
                        [*(-0.58, -0.81, +0.0), *(Star_color)],
                        [*( 0.36, -0.12, +0.0), *(Star_color)],

                        [*(-0.58, -0.81, +0.0), *(Star_color)],
                        [*( 0.95,  0.31, +0.0), *(Star_color)],
                        [*(-0.22,  0.31, +0.0), *(Star_color)],

                        [*( 0.58, -0.81, +0.0), *(Star_color)],
                        [*( 0.22,  0.31, +0.0), *(Star_color)],
                        [*(-0.95,  0.31, +0.0), *(Star_color)],
                    ], dtype=np.float32),
                    shader=ShaderDB.get_instance().get_shader('colored'),
                    render_mode=gl.GL_TRIANGLES
                )
            ]
        )
        super().__init__(*args, **kwargs)

    def _physics_update(self, delta_time: float):
        self.transform.translation.xy += Vec2( 0.01, -(log((self.transform.translation.x+2)))/200 )
        self.rotate(0.1)

    def _on_outside_screen(self, _):
        self.transform.translation.xy = Vec2(-1, np.random.random()*(2)-1)

    def _generate_bounding_box_vertices(self) -> np.ndarray:
        return np.array([
            [-self.star_size*0.95, -self.star_size*0.81, 0.0],
            [ self.star_size*0.95,  self.star_size*0.81, 0.0],
            [-self.star_size*0.95,  self.star_size*0.81, 0.0],
            [ self.star_size*0.95, -self.star_size*0.81, 0.0],
        ])