from dataclasses import dataclass
import math

from utils.geometry import Vec3
from gl_abstractions.texture import Texture, Texture2D

from objects.cube import Cube
from wavefront.model import Model
from wavefront.reader import ModelReader

ALVO_2_MODEL = ModelReader().load_model_from_file('models/alvo2.obj')
ALVO_2_TEXTURE = Texture2D.from_image_path('textures/wood.jpg')

@dataclass
class WoodTarget(Cube):
    model: Model = ALVO_2_MODEL
    texture: Texture = ALVO_2_TEXTURE
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