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
from wavefront.reader import WaveFrontReader
from wavefront.model import Model

DEFAULT_MODEL = WaveFrontReader().load_model_from_file('models/cube.obj')

@dataclass
class Cube(Element):
    model: Model = field(default_factory=lambda: DEFAULT_MODEL)
    shader: Shader = field(default_factory=lambda: ShaderDB.get_instance().get_shader('light_texture'))

    # TODO: Keep texture loaded instead of loading every time
    texture: Texture = field(default_factory=lambda: Texture2D.from_image_path('textures/end_game_loss.png'))
    shape_specs: list[ShapeSpec] = None

    def _init_shape_specs(self):
        vertices_list = self.model.to_unindexed_vertices() # TODO: instead of unindexed, use indices

        has_position = 'a_Position' in [ attr[0] for attr in self.shader.layout.attributes]
        has_texcoord = 'a_TexCoord' in [ attr[0] for attr in self.shader.layout.attributes]
        has_normal = 'a_Normal' in [ attr[0] for attr in self.shader.layout.attributes]

        # # TODO: rename this variable to something less confusing
        vertices_array = np.array([
            # Example Vertex: (posX, posY, posZ, texU, texV, normX, normY, normZ)
            vertex.to_tuple(has_position, has_texcoord, has_normal) for vertex in vertices_list
        ], dtype=np.float32)

        cube_shape = ShapeSpec(
            vertices=vertices_array,
            # indices= TODO: use indices,
            shader=self.shader,
            render_mode=gl.GL_TRIANGLES,
            name=f'{self.name} - Cube',
            texture=self.texture
        )
        self.shape_specs = [ cube_shape ]


    def __post_init__(self):
        self._init_shape_specs()
        super().__post_init__()

    def _physics_update(self, delta_time: float):
        return super()._physics_update(delta_time)
