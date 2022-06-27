from abc import ABC, ABCMeta, abstractmethod
from dataclasses import dataclass, field
from dis import dis
from time import sleep
from typing import TYPE_CHECKING, Union

from utils.geometry import Vec3
from utils.logger import LOGGER
from objects.cube import Cube
from objects.element import PHYSICS_TPS, Element, ShapeSpec
from objects.model_element import ModelElement

if TYPE_CHECKING:
    from objects.world import World

@dataclass
class Ray(Element, metaclass=ABCMeta):
    direction: Vec3 = field(default_factory=lambda: Vec3(0,0,0))
    shape_specs: list[ShapeSpec] = None

    def __post_init__(self):
        self.direction: Union[Vec3, None] = None
        self.shape_specs = self.shape_specs or []
        return super().__post_init__()

    def cast(self, world: 'World', origin: Vec3, direction: Vec3):
        self.transform.translation = origin.xyz
        self.direction = direction.xyz
        from app_vars import APP_VARS
        self.transform.rotation.xyz = APP_VARS.camera.transform.rotation.xyz 
        world.spawn(self)

    def on_spawned(self, world: 'World'):
        if self.direction is None:
            LOGGER.log_warning(f'Trying to spawn a Ray directly! please use the cast() method')
            self.destroy()

        return super().on_spawned(world)

    @abstractmethod
    def _has_hit(self) -> bool:
        '''Please override'''

    @abstractmethod
    def _on_raycast_stopped(self, hit: bool):
        '''Please override'''

    def __stop_raycast(self, hit: bool):
        self.destroy()
        self._on_raycast_stopped(hit=hit)
        self.direction = None

    def _physics_update(self, delta_time: float):
        self.transform.translation.xyz += self.direction * delta_time * PHYSICS_TPS * 0.5
        if self._has_hit():
            self.__stop_raycast(hit=True)

        if self.transform.translation.magnitude() > 60:
            self.__stop_raycast(hit=False)

        return super()._physics_update(delta_time)