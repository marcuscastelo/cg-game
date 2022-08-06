from dataclasses import dataclass
from random import Random, random
from OpenGL import GL as gl
import numpy as np
from numpy import log

from utils.geometry import Vec2, Vec3
from utils.sig import metsig

from objects.element import Element, ElementSpecification, ShapeSpec
from gl_abstractions.shader import ShaderDB
from transform import Transform


@dataclass(init=False)
class LittleStar(Element):
    '''
    Class that defines the little stars, present in the background.
    It does nothing important to the gameplay, only decorates the background
    '''
    # Basic variables that define the little star's visible properties
    star_size: float = 0.004

    @metsig(Element.__init__)
    def __init__(self, *args, **kwargs):

        # Define color pallete to the object Little star
        white: Vec3 = Vec3(255, 255, 255) / 255

        kwargs['specs'] = ElementSpecification(

            # Each little star should spawn with an random angle
            initial_transform=Transform(
                translation=Vec3(0, 0, 0),
                rotation=Vec3(0, 0, np.random.uniform()*2*3.14),
                scale=Vec3(self.star_size, self.star_size, 1) * 3,
            ), # TODO: allow world to set this
            shape_specs=[

                # Little star vertices, making 3 triangles
                ShapeSpec(
                    vertices=np.array([
                        [*( 0.00,  1.00, +0.0), *(white)],
                        [*(-0.58, -0.81, +0.0), *(white)],
                        [*( 0.38, -0.10, +0.0), *(white)],

                        [*(-0.58, -0.81, +0.0), *(white)],
                        [*( 1.00,  0.31, +0.0), *(white)],
                        [*(-0.22,  0.31, +0.0), *(white)],

                        [*( 0.58, -0.70, +0.0), *(white)],
                        [*( 0.22,  0.31, +0.0), *(white)],
                        [*(-0.95,  0.27, +0.0), *(white)],
                    ], dtype=np.float32),
                    shader=ShaderDB.get_instance().get_shader('colored'),
                    render_mode=gl.GL_TRIANGLES
                )
            ]
        )
        
        super().__init__(*args, **kwargs)

    def _physics_update(self, delta_time: float):
        pass

    def _generate_bounding_box_2d_vertices(self) -> np.ndarray:
        return np.array([
            [-self.star_size*0.95, -self.star_size*0.81, 0.0],
            [ self.star_size*0.95,  self.star_size*0.81, 0.0],
            [-self.star_size*0.95,  self.star_size*0.81, 0.0],
            [ self.star_size*0.95, -self.star_size*0.81, 0.0],
        ])