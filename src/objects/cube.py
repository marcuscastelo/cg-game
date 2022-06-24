from cgitb import text
from dataclasses import dataclass, field
import os
import numpy as np
from OpenGL import GL as gl
from utils.geometry import Vec3
from gl_abstractions.shader import Shader, ShaderDB
from gl_abstractions.texture import Texture, Texture2D
from objects.element import Element, ElementSpecification, ShapeSpec
from utils.sig import metsig

from transform import Transform
from objects.wavefront import WaveFrontReader

cube_model = WaveFrontReader().load_model_from_file('./src/objects/pto.obj')
cube_vertices = cube_model.to_unindexed_vertices() # TODO: instead of unindexed, use indices

DEFAULT_TEXTURE = Texture2D.from_image_path('textures/end_game_loss.png')

@dataclass
class Cube(Element):
    shape_specs: list[ShapeSpec] = None  # Initialized in __post_init__
    texture: Texture = field(default=DEFAULT_TEXTURE)

    def _init_shape_specs(self):
        # TODO: rename this variable to something less confusing
        cube_vertices_array = np.array([
            # Example Vertex: (posX, posY, posZ, texU, texV)
            (*vertex.position, *vertex.texture_coords) for vertex in cube_vertices
        ], dtype=np.float32)

        cube_shape = ShapeSpec(
            vertices=cube_vertices_array,
            # indices= TODO: use indices,
            shader=ShaderDB.get_instance().get_shader('textured'),
            render_mode=gl.GL_TRIANGLES,
            name=f'{self.name} - Cube',
            texture=self.texture
        )
        self.shape_specs = [ cube_shape ]


    def __post_init__(self):
        self._init_shape_specs()
        super().__post_init__()
