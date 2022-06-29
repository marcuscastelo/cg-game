from dataclasses import dataclass

from objects.model_element import ModelElement
from wavefront.model import Model
from wavefront.model_reader import ModelReader

MODEL = ModelReader().load_model_from_file('models/target_small.obj')

@dataclass 
class TargetSmall(ModelElement):
    model: Model = MODEL

    @property
    def pseudo_hitbox_distance(self) -> float:
        return self.transform.scale.xy.magnitude() * 1.2