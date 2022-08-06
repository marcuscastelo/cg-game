from dataclasses import dataclass
from gl_abstractions.texture import Texture

from OpenGL import GL as gl

class CubemapTexture(Texture):
    def __init__(self):
        super().__init__(gl.GL_TEXTURE_CUBE_MAP)