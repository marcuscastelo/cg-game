import numpy as np
from OpenGL import GL as gl 
from utils.geometry import Vec3
from gl_abstractions.shader import ShaderDB
from gl_abstractions.texture import Texture2D
from objects.element import Element, ElementSpecification, ShapeSpec
from utils.sig import metsig

from transform import Transform

class Cube(Element):
    @metsig(Element.__init__)
    def __init__(self, *args, **kwargs):
        specification = ElementSpecification (
            initial_transform=Transform (
                translation=Vec3(0, 0, 0),
                rotation=Vec3(0, 0, 0),
                scale=Vec3(1, 1, 1),
            ),
            shape_specs=[
                # TODO: read from Wavefront file
                ShapeSpec(vertices=np.array([
                    ### CUBO 1
                    # Face 1 do Cubo 1 (vértices do quadrado)
                    [*(-1.0, -1.0, +1.0), *(0.0, 0.0)],
                    [*(+1.0, -1.0, +1.0), *(1.0, 0.0)],
                    [*(-1.0, +1.0, +1.0), *(0.0, 1.0)],
                    [*(+1.0, +1.0, +1.0), *(1.0, 1.0)],

                    # Face 2 do Cubo 1
                    [*(+1.0, -1.0, -1.0), *(0.0, 0.0)],
                    [*(+1.0, +1.0, -1.0), *(1.0, 0.0)],
                    [*(+1.0, -1.0, +1.0), *(0.0, 1.0)],
                    [*(+1.0, +1.0, +1.0), *(1.0, 1.0)],
                    
                    # Face 3 do Cubo 1
                    [*(-1.0, -1.0, -1.0), *(0.0, 0.0)],
                    [*(-1.0, +1.0, -1.0), *(1.0, 0.0)],
                    [*(+1.0, -1.0, -1.0), *(0.0, 1.0)],
                    [*(+1.0, +1.0, -1.0), *(1.0, 1.0)],

                    # Face 4 do Cubo 1
                    [*(-1.0, -1.0, -1.0), *(0.0, 0.0)],
                    [*(-1.0, -1.0, +1.0), *(1.0, 0.0)],
                    [*(-1.0, +1.0, -1.0), *(0.0, 1.0)],
                    [*(-1.0, +1.0, +1.0), *(1.0, 1.0)],

                    # Face 5 do Cubo 1
                    [*(-1.0, -1.0, -1.0), *(0.0, 0.0)],
                    [*(-1.0, -1.0, +1.0), *(1.0, 0.0)],
                    [*(+1.0, -1.0, -1.0), *(0.0, 1.0)],
                    [*(+1.0, -1.0, +1.0), *(1.0, 1.0)],
                    
                    # Face 6 do Cubo 1
                    [*(-1.0, +1.0, -1.0), *(0.0, 0.0)],
                    [*(-1.0, +1.0, +1.0), *(1.0, 0.0)],
                    [*(+1.0, +1.0, -1.0), *(0.0, 1.0)],
                    [*(+1.0, +1.0, +1.0), *(1.0, 1.0)],

                ], dtype=np.float32),
                shader=ShaderDB.get_instance().get_shader('textured'),
                render_mode=gl.GL_TRIANGLE_STRIP,
                name='Cube',
                texture=Texture2D.from_image_path('textures/end_game_loss.png'),
            ),
            ]
        )
        kwargs['specs'] = specification
        super().__init__(*args, **kwargs)

    def _physics_update(self, delta_time: float):

        self.transform.scale.x *= 1.01

        return super()._physics_update(delta_time)