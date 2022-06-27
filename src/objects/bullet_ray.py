from dataclasses import dataclass
from typing import TYPE_CHECKING

from utils.geometry import Vec3
from utils.logger import LOGGER
from objects.cube import Cube
from objects.element import Element
from objects.ray import Ray
from wavefront.material import Material

if TYPE_CHECKING:
    from objects.world import World

@dataclass
class BulletRay(Ray):
    show_debug_cube: bool = False
    def __post_init__(self):
        if self.show_debug_cube:
            a = Cube('SelectionRayCube')
            self.transform.scale.xyz = Vec3(0.1,0.1,3) * 0.3

            self.shape_specs = a.shape_specs
            a.shape_specs[0].material = Material('GunShot',Ka=Vec3(1,0,0),Kd=Vec3(1,0,0))
        super().__post_init__()

    def on_spawned(self, world: 'World'):
        self.destroyable_elements = world.elements
        return super().on_spawned(world)

    def _has_hit(self) -> bool:
        self.destroyable_elements = [ element for element in self.destroyable_elements if element.ray_destroyable ]

        def calc_distance(element: Element) -> float:
            try:
                difference = element.center.xyz - self.center.xyz
            except AttributeError as e:
                print(f'{element=}')
                raise e 
            distance = difference.magnitude()
            return distance

        distances = [ calc_distance(element) for element in self.destroyable_elements ]

        # def stop_raycast():
        #         self.direction = Vec3(0,0,0)
        #         self.transform.translation.xyz = Vec3(0,100,0)
        #         keep_iterating = False

        sorted_pairs = sorted(zip(distances, self.destroyable_elements), key=lambda a: a[0])
        if sorted_pairs:
            element = sorted_pairs[0][1]
            distance = sorted_pairs[0][0]

            if distance < element.pseudo_hitbox_distance:
                self.hit_element = element
                return True

        self.hit_element = None
        return False

    def _on_raycast_stopped(self, hit: bool):
        LOGGER.log_debug('Stopped!')
        from app_vars import APP_VARS
        if not hit:
            return
        
        assert self.hit_element

        LOGGER.log_debug(f'Bullet hit element {self.hit_element.name}')
        LOGGER.log_debug(f'{self.hit_element.ray_destroyable=}')
        self.hit_element.destroy()

        return super()._on_raycast_stopped(hit)

    def _physics_update(self, delta_time: float):
        self.transform.scale.z *= 1 + (0.1 * delta_time)

        return super()._physics_update(delta_time)