from dataclasses import dataclass
from OpenGL import GL as gl
from math import atan2, cos, sin
import numpy as np

from utils.geometry import Vec2, Vec3
from utils.sig import metsig

from objects.element import Element, ElementSpecification, ShapeSpec
from gl_abstractions.shader import ShaderDB
from transform import Transform


@dataclass(init=False)
class Star(Element):
    
    # Basic variables that define the star's visible properties
    star_size: float = 0.02
    rotation_speed: float = 0.1
    speed_vec = Vec2( 0.01, 0.01)

    @metsig(Element.__init__)
    def __init__(self, *args, **kwargs):

        yellow: Vec3 = Vec3(230, 230, 0.0) / 255 * 0.7
        dark_yellow: Vec3 = Vec3(200, 200, 0.0) / 255 * 0.7

        kwargs['specs'] = ElementSpecification(
            initial_transform=Transform(
                translation=Vec3(0, 0, 0),
                rotation=Vec3(0, 0, 0),
                scale=Vec3(self.star_size, self.star_size, 1) * 3,
            ), # TODO: allow world to set this
            shape_specs=[

                # These vertices were based on a pentagram,
                # consisting of 3 triangles and 3 lines intersection
                ShapeSpec(
                    vertices=np.array([
                        [*( 0.00,  1.00, +0.0), *(yellow)],
                        [*(-0.58, -0.81, +0.0), *(yellow)],
                        [*( 0.36, -0.12, +0.0), *(yellow)],

                        [*(-0.58, -0.81, +0.0), *(dark_yellow)],
                        [*( 0.95,  0.31, +0.0), *(yellow)],
                        [*(-0.22,  0.31, +0.0), *(yellow)],

                        [*( 0.58, -0.81, +0.0), *(dark_yellow)],
                        [*( 0.22,  0.31, +0.0), *(dark_yellow)],
                        [*(-0.95,  0.31, +0.0), *(dark_yellow)],
                    ], dtype=np.float32),
                    shader=ShaderDB.get_instance().get_shader('colored'),
                    render_mode=gl.GL_TRIANGLES
                )
            ]
        )
        super().__init__(*args, **kwargs)

    def _physics_update(self, delta_time: float):
        self.transform.translation.xy += self.speed_vec * delta_time * 50
        self.transform.rotation.z += self.rotation_speed

        super()._physics_update(delta_time)

    def _on_outside_screen(self):
        # min_x, max_x, min_y, max_y = self.get_bounding_box()
        # min_x, min_y, max_x, max_y = self.get_bounding_box()
        min_x, min_y, max_x, max_y = (*self.transform.translation.xy, *self.transform.translation.xy)
        if min_x < -1 or max_x > 1:
            self.speed_vec.x *= -1
        if min_y < -1 or max_y > 1:
            self.speed_vec.y *= -1

        print(f'{self.speed_vec}')
        

    def _generate_bounding_box_2d_vertices(self) -> np.ndarray:
        return np.array([
            [-self.star_size*0.95, -self.star_size*0.81, 0.0],
            [ self.star_size*0.95,  self.star_size*0.81, 0.0],
            [-self.star_size*0.95,  self.star_size*0.81, 0.0],
            [ self.star_size*0.95, -self.star_size*0.81, 0.0],
        ])