from dataclasses import dataclass

from utils.geometry import Vec3
from objects.model_element import ModelElement
from wavefront.model import Model
from wavefront.reader import ModelReader

BOT_MODEL = ModelReader().load_model_from_file('models/bot.obj')

@dataclass
class Bot(ModelElement):
    model: Model = BOT_MODEL

    @property
    def center(self) -> Vec3:
        return self.transform.translation + Vec3(0, 0.5, 0) * self.transform.scale

    @property
    def pseudo_hitbox_distance(self) -> float:
        return super().pseudo_hitbox_distance * 0.5