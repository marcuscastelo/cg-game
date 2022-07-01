from abc import ABCMeta, abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Union

from utils.geometry import Vec3
from utils.logger import LOGGER
from objects.element import PHYSICS_TPS, Element, ShapeSpec

if TYPE_CHECKING:
    from objects.world import World

@dataclass
class Ray(Element, metaclass=ABCMeta):
    direction: Vec3 = field(default_factory=lambda: Vec3(0,0,0))
    shape_specs: list[ShapeSpec] = None
    ray_selectable: bool = False
    ray_destroyable: bool = False

    def __post_init__(self):
        self.direction: Union[Vec3, None] = None
        self.shape_specs = self.shape_specs or []
        return super().__post_init__()

    def cast(self, world: 'World', origin: Vec3, direction: Vec3):
        ''' Casts a ray from the origin to the direction '''

        self.transform.translation = origin.xyz
        self.direction = direction.xyz
        from app_vars import APP_VARS
        self.transform.rotation.xyz = APP_VARS.camera.transform.rotation.xyz 
        world.spawn(self)

    def on_spawned(self, world: 'World'):
        ''' Overrides Element method '''

        if self.direction is None:
            # Rays should not be spawned directly, instead use the cast method
            # Example: Ray(name='MyAwesomeRay').cast(...)
            LOGGER.log_warning(f'Trying to spawn a Ray directly! please use the cast() method')
            self.destroy()

        return super().on_spawned(world)

    @abstractmethod
    def _has_hit(self) -> bool:
        ''' Virtual method to determine if the ray has hit something '''
        pass
        
    @abstractmethod
    def _on_raycast_stopped(self, hit: bool):
        ''' Virtual method to handle the raycast stopping (either because it hit something or some other reason, such as the ray being out of range) '''
        pass

    def __stop_raycast(self, hit: bool):
        ''' Stops the raycast and calls the on_raycast_stopped method (do not override or call this method directly outside of the class) '''
        self.destroy()
        self._on_raycast_stopped(hit=hit)
        self.direction = None

    def _physics_update(self, delta_time: float):
        ''' Overrides Element method '''
        # Move the ray based on the direction
        self.transform.translation.xyz += self.direction * delta_time * PHYSICS_TPS * 0.5

        # Check if the ray has hit something
        if self._has_hit():
            self.__stop_raycast(hit=True)

        # Check if the ray has gone out of range
        if self.transform.translation.magnitude() > 60:
            self.__stop_raycast(hit=False)

        return super()._physics_update(delta_time)

    # TODO: move collision checking of SelectionRay and BulletRay to here (and then to PhysicsSystem, someday)