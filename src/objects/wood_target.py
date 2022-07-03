from dataclasses import dataclass, field
import math

from gl_abstractions.texture import Texture, Texture2D

from objects.cube import Cube
from wavefront.model import Model
from wavefront.model_reader import ModelReader

ALVO_2_MODEL = ModelReader().load_model_from_file('models/alvo2.obj')
ALVO_2_TEXTURE = None 
def get_tex():
    # TODO: remove this and make a TextureDB and ModelDB
    
    # Load it after WoodTarget instantiation because Texture2D needs an OpenGL context to be created
    global ALVO_2_TEXTURE
    if ALVO_2_TEXTURE is None:
        ALVO_2_TEXTURE = Texture2D.from_image_path('textures/wood.jpg')

    return ALVO_2_TEXTURE

@dataclass
class WoodTarget(Cube):
    ''' An element that represents a wood target. '''
    model: Model = field(default_factory= lambda: ALVO_2_MODEL)
    texture: Texture = field(default_factory=get_tex)
    ray_selectable: bool = True
    ray_destroyable: bool = True
    
    def __post_init__(self):
        self.transform.scale *= 0.3
        self.transform.scale.xy *= 1
        self.transform.rotation.y = math.pi/2
        return super().__post_init__()

    @property
    def pseudo_hitbox_distance(self) -> float:
        return self.transform.scale.xy.magnitude()