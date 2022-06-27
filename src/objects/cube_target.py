from dataclasses import dataclass
import math

from utils.geometry import Vec3

from objects.cube import Cube


@dataclass
class CubeTarget(Cube):
    def __post_init__(self):
        self.transform.scale *= 0.3
        self.transform.scale.z *= -1
        self.transform.scale.xy *= 3
        return super().__post_init__()

    @property
    def pseudo_hitbox_distance(self) -> float:
        return self.transform.scale.xy.magnitude() / math.sqrt(2) * 0.7