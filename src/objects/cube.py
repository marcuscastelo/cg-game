from dataclasses import dataclass

from objects.model_element import ModelElement
from wavefront.model import Model
from wavefront.reader import ModelReader

CUBE_MODEL = ModelReader().load_model_from_file('models/cube.obj')

@dataclass
class Cube(ModelElement):
    model: Model = CUBE_MODEL