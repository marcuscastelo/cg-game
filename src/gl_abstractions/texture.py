from abc import ABCMeta
from dataclasses import dataclass, field
import imageio
from utils.sig import metsig
import glfw
from OpenGL import GL as gl
import numpy as np

@dataclass
class TextureParameters:
    ''' OpenGL Parameters for a texture '''
    wrap_s: int = gl.GL_CLAMP_TO_BORDER
    wrap_t: int = gl.GL_CLAMP_TO_BORDER
    min_filter: int = gl.GL_LINEAR
    mag_filter: int = gl.GL_LINEAR
    internal_format: int = gl.GL_RGB
    format: int = gl.GL_RGB
    type: int = gl.GL_UNSIGNED_BYTE

@dataclass
class Texture:
    '''
    Base class for all textures.
    When instantiated, a texture is created in OpenGL and its parameters are set.
    '''
    texture_type: int
    texture_parameters: TextureParameters = field(default_factory=TextureParameters)
    
    def __post_init__(self):
        assert glfw.get_current_context() is not None, 'Must call `glfw.init()` before creating a texture'
        assert isinstance(self.texture_type, int), f"Texture type expected to be int, but found '{type(self.texture_type)}'"
        assert isinstance(self.texture_parameters, TextureParameters), f"Texture type expected to be TextureParameters, but found '{type(self.texture_parameters)}'"

        self.texture_type = self.texture_type
        self.id = gl.glGenTextures(1)
        self._upload_parameters()
        pass

    def bind(self) -> None:
        gl.glBindTexture(self.texture_type, self.id)
    
    def unbind(self) -> None:
        gl.glBindTexture(self.texture_type, 0)

    def _upload_parameters(self):
        self.bind()
        gl.glTexParameteri(self.texture_type, gl.GL_TEXTURE_WRAP_S, self.texture_parameters.wrap_s)
        gl.glTexParameteri(self.texture_type, gl.GL_TEXTURE_WRAP_T, self.texture_parameters.wrap_t)
        gl.glTexParameteri(self.texture_type, gl.GL_TEXTURE_MIN_FILTER, self.texture_parameters.min_filter)
        gl.glTexParameteri(self.texture_type, gl.GL_TEXTURE_MAG_FILTER, self.texture_parameters.mag_filter)
        self.unbind()    

@dataclass
class Texture2D(Texture):
    '''
    Specialized texture class for 2D textures.
    '''
    texture_type: int = gl.GL_TEXTURE_2D

    @classmethod
    def from_image_path(cls, image_path: str, tex2d_params: TextureParameters = None) -> 'Texture2D':
        ''' Loads a 2D texture from a image file '''
        image = np.array(imageio.imread(image_path))[::-1,:,:]

        # TODO: support RGBA
        if image.shape[2] == 4: # if image is RGBA (png)
            image = image[:,:,:3] # remove alpha channel and remove last column

        obj = Texture2D(
            # texture_type=gl.GL_TEXTURE_2D,
            # texture_parameters=tex2d_params
        )
        obj.upload_raw_texture(image)
        return obj

    def upload_raw_texture(self, texture: np.ndarray) -> None:
        ''' Uploads a raw texture to the GPU '''
        self.bind()
        gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, self.texture_parameters.internal_format, texture.shape[1], texture.shape[0], 0, self.texture_parameters.format, self.texture_parameters.type, texture)
        self.unbind()