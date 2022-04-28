from dataclasses import dataclass
import imageio
from utils.sig import metsig

from OpenGL import GL as gl
import numpy as np

class Texture:
    def __init__(self):
        self.id = gl.glGenTextures(1)
        pass


@dataclass
class Texture2DParameters:
    wrap_s: int = gl.GL_CLAMP_TO_BORDER
    wrap_t: int = gl.GL_CLAMP_TO_BORDER
    min_filter: int = gl.GL_LINEAR
    mag_filter: int = gl.GL_LINEAR
    internal_format: int = gl.GL_RGB
    format: int = gl.GL_RGB
    type: int = gl.GL_UNSIGNED_BYTE

class Texture2D(Texture):
    def __init__(self, tex2d_params: Texture2DParameters = None):
        super().__init__()
        self.params = tex2d_params if tex2d_params is not None else Texture2DParameters()
        self._upload_parameters()

    @classmethod
    def from_image_path(cls, image_path: str, tex2d_params: Texture2DParameters = None) -> 'Texture2D':
        image = np.array(imageio.imread(image_path))[::-1,:,:]

        # TODO: support RGBA
        if image.shape[2] == 4: # if image is RGBA (png)
            image = image[:,:-1,:3] # remove alpha channel and remove last column
        

        obj = cls(tex2d_params=tex2d_params)
        obj.upload_raw_texture(image)
        return obj

    def _upload_parameters(self):
        self.bind()
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, self.params.wrap_s)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, self.params.wrap_t)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, self.params.min_filter)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, self.params.mag_filter)
        self.unbind()

    def upload_raw_texture(self, texture: np.ndarray) -> None:
        self.bind()
        gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, self.params.internal_format, texture.shape[1], texture.shape[0], 0, self.params.format, self.params.type, texture)
        self.unbind()

    def bind(self) -> None:
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.id)

    def unbind(self) -> None:
        gl.glBindTexture(gl.GL_TEXTURE_2D, 0)