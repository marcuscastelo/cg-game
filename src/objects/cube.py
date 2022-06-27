from dataclasses import dataclass

from utils.geometry import Vec3

from objects.model_element import ModelElement
from wavefront.model import Model
from wavefront.reader import ModelReader

CUBE_MODEL = ModelReader().load_model_from_file('models/cube.obj')

@dataclass
class Cube(ModelElement):
    model: Model = CUBE_MODEL

    @property
    def center(self) -> Vec3:
        return self.transform.translation.xyz + Vec3(0,0.5,0) * self.transform.scale.y