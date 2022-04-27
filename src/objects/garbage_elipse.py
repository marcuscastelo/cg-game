from dataclasses import dataclass
from OpenGL import GL as gl
import numpy as np
from numpy import log

from utils.geometry import Vec2, Vec3
from utils.sig import metsig

from objects.element import Element, ElementSpecification, ShapeSpec
from shader import Shader
from transformation_matrix import Transform


@dataclass(init=False)
class Garbage_Elipse(Element):
    rotation_speed: float = 0.01

    # def _create_vertex_buffer(self) -> VertexSpecification:
    #     self.shader = Shader('shaders/simple_red.vert', 'shaders/simple_red.frag') #TODO - Change this. Too costly, and unpratical
    #     return VertexSpecification([
    #         Vertex(Vec3(0.000, 0.0375, 0.0)),
    #         Vertex(Vec3(-0.015, 0.000, 0.0)),
    #         Vertex(Vec3(0.015, 0.0, 0.0)),

    #         Vertex(Vec3(0.015, 0.000, 0.0)),
    #         Vertex(Vec3(-0.015, 0.000, 0.0)),
    #         Vertex(Vec3(0.000, -0.0375, 0.0)),
            
           
            
    #     ])


    

    @metsig(Element.__init__)
    def __init__(self, *args, **kwargs):
        kwargs['specs'] = ElementSpecification(
            initial_transform=Transform(
                translation=Vec3(0, 0, 0),
                rotation=Vec3(0, 0, 0),
                scale=Vec3(1, 1, 1),
            ),
            shape_specs=[
                ShapeSpec(
                    vertices=np.array([
                        *(0.000, 0.0375, +0.0),
                        *(-0.015, 0.000, +0.0),
                        *(0.015, 0.0, +0.0),

                        *(0.015, 0.000, +0.0),
                        *(-0.015, 0.000, +0.0),
                        *(0.000, -0.0375, +0.0),
                    ], dtype=np.float32),
                    render_mode=gl.GL_TRIANGLE_STRIP
                )
            ]
        )

        super().__init__(*args, **kwargs)

    def _physics_update(self, delta_time: float):
        self.rotate(self.rotation_speed)
