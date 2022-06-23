import os
import numpy as np
from OpenGL import GL as gl 
from utils.geometry import Vec3
from gl_abstractions.shader import ShaderDB
from gl_abstractions.texture import Texture, Texture2D
from objects.element import Element, ElementSpecification, ShapeSpec
from utils.sig import metsig

from transform import Transform
from objects.wavefront import WaveFrontReader

cube_model = WaveFrontReader().load_model_from_file('./src/objects/caixa2.obj')
cube_vertices = cube_model.to_raw_vertices()

class Cube(Element):
    @metsig(Element.__init__)
    def __init__(self, *args, custom_texture: Texture = None, **kwargs):
        specification = ElementSpecification (
            initial_transform=Transform (
                translation=Vec3(0, 0, 0),
                rotation=Vec3(0, 0, 0),
                scale=Vec3(1, 1, 1),
            ),
            shape_specs=[
                # TODO: read from Wavefront file
                ShapeSpec(vertices=np.array([
                    (*vertex.position, *vertex.texture_coords) for vertex in cube_vertices 
                ], dtype=np.float32),
                shader=ShaderDB.get_instance().get_shader('textured'),
                render_mode=gl.GL_TRIANGLES,
                name='Cube',
                texture=custom_texture or Texture2D.from_image_path('textures/end_game_loss.png'),
            ),
            ]
        )
        kwargs['specs'] = specification
        super().__init__(*args, **kwargs)