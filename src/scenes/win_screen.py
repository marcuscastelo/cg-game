import imageio
from utils.geometry import Vec3
from utils.sig import metsig
from gl_abstractions.texture import Texture2D
from objects.element import Element, ElementSpecification, ShapeSpec

from OpenGL import GL as gl
import numpy as np

from transformation_matrix import Transform

from shader import ShaderDB

class Screen(Element):
    @metsig(Element.__init__)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    pass

_WIN_IMAGE = imageio.imread('textures/end_game_message.png')

class WinScreen(Element):
    @metsig(Screen.__init__)
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
                        *(-1.0, -0.75, 0.0), *(0.0, 0.0),
                        *( 1.0, -0.75, 0.0), *(1.0, 0.0),
                        *(-1.0,  0.75, 0.0), *(0.0, 1.0),
                        *( 1.0, -0.75, 0.0), *(1.0, 0.0),
                        *( 1.0,  0.75, 0.0), *(1.0, 1.0),
                        *(-1.0,  0.75, 0.0), *(0.0, 1.0),

                    ], dtype=np.float32),
                    # shader=ShaderDB.get_instance().get_shader('simple_red'),
                    shader=ShaderDB.get_instance().get_shader('textured'),
                    texture=Texture2D.from_image_path('textures/end_game_message.png'),
                    name='Win Screen',
                )
            ]
        )

        super().__init__(*args, **kwargs)

    def _get_bounding_box_vertices(self) -> np.ndarray:
        return np.array([
            [-1.0, -1.0, 0.0],
            [+1.0, -1.0, 0.0],
            [+1.0, +1.0, 0.0],
            [-1.0, +1.0, 0.0],
        ], dtype=np.float32)
        