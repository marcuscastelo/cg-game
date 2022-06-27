from dataclasses import dataclass
from typing import TYPE_CHECKING

from utils.geometry import Vec3
from utils.logger import LOGGER
from objects.cube import Cube
from objects.element import Element
from objects.ray import Ray

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
        super().__post_init__()

    def on_spawned(self, world: 'World'):
        from app_vars import APP_VARS
        self.selectable_elements = world.elements
        return super().on_spawned(world)

    def _has_hit(self) -> bool:
        self.selectable_elements = [ element for element in self.selectable_elements if element.ray_selectable ]

        def calc_distance(element: Element) -> float:
            difference = element.transform.translation.xyz - self.transform.translation.xyz
            difference = difference * element.transform.scale.xyz
            # if element._state.selected:
            #     scaled_difference /= 2 # FIXME: hardcoded value

            distance = difference.magnitude()
            return distance

        distances = [ calc_distance(element) for element in self.selectable_elements ]

        # def stop_raycast():
        #         self.direction = Vec3(0,0,0)
        #         self.transform.translation.xyz = Vec3(0,100,0)
        #         keep_iterating = False

        sorted_pairs = sorted(zip(distances, self.selectable_elements), key=lambda a: a[0])
        if sorted_pairs:
            element = sorted_pairs[0][1]
            distance = sorted_pairs[0][0]

            if distance < 1:
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
        self.hit_element.destroy()

        return super()._on_raycast_stopped(hit)

    def _physics_update(self, delta_time: float):
        LOGGER.log_debug(f'updating {delta_time}')
        self.transform.scale.z *= 1 + (0.1 * delta_time)

        return super()._physics_update(delta_time)