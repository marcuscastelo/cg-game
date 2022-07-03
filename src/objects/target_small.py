from dataclasses import dataclass

from objects.model_element import ModelElement
from wavefront.model import Model
from wavefront.model_reader import ModelReader

TARGET_SMALL_MODEL = ModelReader().load_model_from_file('models/target_small.obj')

@dataclass 
class TargetSmall(ModelElement):
    model: Model = TARGET_SMALL_MODEL

    @property
    def pseudo_hitbox_distance(self) -> float:
        ''' Override of Element property. '''
        # Special value to make the target be more hitable
        return self.transform.scale.xy.magnitude() * 1.2 