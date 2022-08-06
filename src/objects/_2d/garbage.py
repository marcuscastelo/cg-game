from dataclasses import dataclass
import numpy as np

from utils.geometry import Vec2, Vec3
from utils.sig import metsig

from objects.element import Element, ElementSpecification, ShapeSpec
from gl_abstractions.shader import ShaderDB
from transform import Transform

from OpenGL import GL as gl


@dataclass(init=False)
class Garbage(Element):
    '''
    Class that represents the garbage floating in the space (screen).
    All must be collected so the player can win.
    '''
    # Basic variables that define the garbage's visible properties
    rotation_speed: float = 0.01

    @metsig(Element.__init__)
    def __init__(self, *args, **kwargs):
        
        # Define color pallete to the object Garbage
        garbage_color: Vec3 = Vec3(119, 119, 119) / 255
        dark_garbage_color: Vec3 = Vec3(80, 80, 80) / 255
        diamond_color: Vec3 = Vec3(204, 204, 204) / 255
        kwargs['specs'] = ElementSpecification(
            initial_transform=Transform(
                translation=Vec3(0, 0, 0),
                rotation=Vec3(0, 0, 0),
                scale=Vec3(1, 1, 1),
            ),
            shape_specs=[
                # Garbage outer draw
                ShapeSpec(
                    vertices=np.array([
                        [*(-0.025, -0.040, +0.0), *(garbage_color),],
                        [*( 0.025, -0.040, +0.0), *(dark_garbage_color),],
                        [*(-0.025,  0.040, +0.0), *(garbage_color),],
                        [*(-0.025,  0.040, +0.0), *(garbage_color),],
                        [*( 0.025, -0.040, +0.0), *(dark_garbage_color),],
                        [*( 0.025,  0.040, +0.0), *(dark_garbage_color),],
                    ], dtype=np.float32),
                    shader=ShaderDB.get_instance().get_shader('colored'),
                ),

                # Garbage inner draw
                ShapeSpec(
                    vertices=np.array([
                        [*(0.000, 0.0375, +0.0), *(diamond_color)],
                        [*(-0.015, 0.000, +0.0), *(diamond_color)],
                        [*(0.015, 0.0, +0.0), *(diamond_color)],

                        [*(0.015, 0.000, +0.0), *(diamond_color)],
                        [*(-0.015, 0.000, +0.0), *(diamond_color)],
                        [*(0.000, -0.0375, +0.0), *(diamond_color)],
                    ], dtype=np.float32),
                    render_mode=gl.GL_TRIANGLE_STRIP,
                    shader=ShaderDB.get_instance().get_shader('colored'),
                )
            ]
        )

        super().__init__(*args, **kwargs)

    def _generate_bounding_box_2d_vertices(self) -> np.ndarray:
        return np.array([
            [*(-0.025, -0.040, +0.0)],
            [*( 0.025, -0.040, +0.0)],
            [*( 0.025,  0.040, +0.0)],
            [*(-0.025,  0.040, +0.0)],
        ])

    def _physics_update(self, delta_time: float):
        self.transform.rotation.z += self.rotation_speed
        super()._physics_update(delta_time)
