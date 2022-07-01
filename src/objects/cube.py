from dataclasses import dataclass

from utils.geometry import Vec3

from objects.model_element import ModelElement
from wavefront.model import Model
from wavefront.model_reader import ModelReader

CUBE_MODEL = ModelReader().load_model_from_file('models/cube.obj')

@dataclass
class Cube(ModelElement):
    ''' An element that represents a cube. '''
    model: Model = CUBE_MODEL # Pre-loaded model

    @property
    def center(self) -> Vec3:
        # The cube.obj model is centered at the origin on x and z, but not on y.
        return self.transform.translation.xyz + Vec3(0,0.5,0) * self.transform.scale.y