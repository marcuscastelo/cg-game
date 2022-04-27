from dataclasses import dataclass
from OpenGL import GL as gl
import numpy as np
from numpy import log

from utils.geometry import Vec2, Vec3
from utils.sig import metsig

from objects.element import Element, ElementSpecification, ShapeSpec
from transformation_matrix import Transform


@dataclass(init=False)
class Satellite(Element):
    rotation_speed: float = 0.005

    # def _create_vertex_buffer(self) -> VertexSpecification:
    #     return VertexSpecification([
    #         Vertex(Vec3(-0.04, 0.05, 0.0)),
    #         Vertex(Vec3(0.04, -0.05, 0.0)),
    #         Vertex(Vec3(0.04, 0.05, 0.0)),

    #         Vertex(Vec3(-0.04, 0.05, 0.0)),
    #         Vertex(Vec3(-0.04, -0.05, 0.0)),
    #         Vertex(Vec3(0.04, -0.05, 0.0)),

    #         Vertex(Vec3(0.04, 0.01, 0.0)),
    #         Vertex(Vec3(0.08, -0.01, 0.0)),
    #         Vertex(Vec3(0.08, 0.01, 0.0)),

    #         Vertex(Vec3(0.08, -0.01, 0.0)),
    #         Vertex(Vec3(0.04, 0.01, 0.0)),
    #         Vertex(Vec3(0.04, -0.01, 0.0)),

    #         Vertex(Vec3(0.08, 0.02, 0.0)),
    #         Vertex(Vec3(0.1, -0.02, 0.0)),
    #         Vertex(Vec3(0.1, 0.02, 0.0)),

    #         Vertex(Vec3(0.08, 0.02, 0.0)),
    #         Vertex(Vec3(0.08, -0.02, 0.0)),
    #         Vertex(Vec3(0.1, -0.02, 0.0)),

    #         ##

    #         Vertex(Vec3(-0.04, 0.01, 0.0)),
    #         Vertex(Vec3(-0.08, -0.01, 0.0)),
    #         Vertex(Vec3(-0.08, 0.01, 0.0)),

    #         Vertex(Vec3(-0.08, -0.01, 0.0)),
    #         Vertex(Vec3(-0.04, 0.01, 0.0)),
    #         Vertex(Vec3(-0.04, -0.01, 0.0)),

    #         Vertex(Vec3(-0.08, 0.02, 0.0)),
    #         Vertex(Vec3(-0.1, -0.02, 0.0)),
    #         Vertex(Vec3(-0.1, 0.02, 0.0)),

    #         Vertex(Vec3(-0.08, 0.02, 0.0)),
    #         Vertex(Vec3(-0.08, -0.02, 0.0)),
    #         Vertex(Vec3(-0.1, -0.02, 0.0)),
    #     ])

    @metsig(Element.__init__)
    def __init__(self, *args, **kwargs):
        self._render_primitive = gl.GL_TRIANGLES

        kwargs['specs'] = ElementSpecification(
            initial_transform=Transform(
                translation=Vec3(0, 0, 0),
                rotation=Vec3(0, 0, 0),
                scale=Vec3(1, 1, 1),
            ), # TODO: allow world to set this
            shape_specs=[
                ShapeSpec(
                    vertices=np.array([
                        *(-0.04, 0.05, 0.0), # *(0.0, 0.0),
                        *(0.04, -0.05, 0.0), # *(0.0, 0.0),
                        *(0.04, 0.05, 0.0), # *(0.0, 0.0),

                        *(-0.04, 0.05, 0.0), # *(0.0, 0.0),
                        *(-0.04, -0.05, 0.0), # *(0.0, 0.0),
                        *(0.04, -0.05, 0.0), # *(0.0, 0.0),

                        *(0.04, 0.01, 0.0), # *(0.0, 0.0),
                        *(0.08, -0.01, 0.0), # *(0.0, 0.0),
                        *(0.08, 0.01, 0.0), # *(0.0, 0.0),

                        *(0.08, -0.01, 0.0), # *(0.0, 0.0),
                        *(0.04, 0.01, 0.0), # *(0.0, 0.0),
                        *(0.04, -0.01, 0.0), # *(0.0, 0.0),

                        *(0.08, 0.02, 0.0), # *(0.0, 0.0),
                        *(0.1, -0.02, 0.0), # *(0.0, 0.0),
                        *(0.1, 0.02, 0.0), # *(0.0, 0.0),

                        *(0.08, 0.02, 0.0), # *(0.0, 0.0),
                        *(0.08, -0.02, 0.0), # *(0.0, 0.0),
                        *(0.1, -0.02, 0.0), # *(0.0, 0.0),

                        ##

                        *(-0.04, 0.01, 0.0), # *(0.0, 0.0),
                        *(-0.08, -0.01, 0.0), # *(0.0, 0.0),
                        *(-0.08, 0.01, 0.0), # *(0.0, 0.0),

                        *(-0.08, -0.01, 0.0), # *(0.0, 0.0),
                        *(-0.04, 0.01, 0.0), # *(0.0, 0.0),
                        *(-0.04, -0.01, 0.0), # *(0.0, 0.0),

                        *(-0.08, 0.02, 0.0), # *(0.0, 0.0),
                        *(-0.1, -0.02, 0.0), # *(0.0, 0.0),
                        *(-0.1, 0.02, 0.0), # *(0.0, 0.0),

                        *(-0.08, 0.02, 0.0), # *(0.0, 0.0),
                        *(-0.08, -0.02, 0.0), # *(0.0, 0.0),
                        *(-0.1, -0.02, 0.0), # *(0.0, 0.0),
                    ], dtype=np.float32),
                    render_mode=gl.GL_TRIANGLE_STRIP
                )
            ]
        )

        super().__init__(*args, **kwargs)

    def _physics_update(self, delta_time: float):
        self.rotate(self.rotation_speed)
