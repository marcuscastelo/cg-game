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
    ''' A bullet ray is a ray that can hit an element and destroy it if it is destroyable by rays. '''
    show_debug_cube: bool = False

    def __post_init__(self):
        if self.show_debug_cube:
            a = Cube('SelectionRayCube')
            self.transform.scale.xyz = Vec3(0.1,0.1,3) * 0.3

            self.shape_specs = a.shape_specs
            # TODO: make .mtl
            a.shape_specs[0].material = Material('GunShot',Ka=Vec3(1,0,0),Kd=Vec3(1,0,0))
        super().__post_init__()

    def on_spawned(self, world: 'World'):
        ''' Override of Element method. '''
        from app_vars import APP_VARS
        
        # Get a reference of world elements to be used in the raycast later
        APP_VARS.last_bullet = self
        self.destroyable_elements = world.elements
        return super().on_spawned(world)

    def _has_hit(self) -> bool:
        ''' Override of Ray method. '''

        # Filter out elements that are not destroyable
        self.destroyable_elements = [ element for element in self.destroyable_elements if element.ray_destroyable ]

        def calc_distance(element: Element) -> float:
            ''' Calculate the distance between the ray and the element. '''
            difference = element.center.xyz - self.center.xyz
            distance = difference.magnitude()
            return distance

        # Calculate the distance between the ray and each element
        distances = [ calc_distance(element) for element in self.destroyable_elements ]

        # Sort the pairs by distance
        sorted_pairs = sorted(zip(distances, self.destroyable_elements), key=lambda a: a[0])
        if sorted_pairs:
            # Get the element with the shortest distance
            element = sorted_pairs[0][1]
            distance = sorted_pairs[0][0]

            if distance < element.pseudo_hitbox_distance:
                # If the distance is less than the element's hitbox distance, then the ray has hit the element
                self.hit_element = element
                return True

        # If there are no pairs, then the ray has not hit anything
        self.hit_element = None
        return False

    def _on_raycast_stopped(self, hit: bool):
        LOGGER.log_debug('BulletRay Stopped!')
        from app_vars import APP_VARS

        if not hit:
            # If the ray has not hit anything, then destroy the bullet
            # FIXME: super() is not called!!! (this is a bug, probably)
            return
        
        assert self.hit_element, f'{hit=} (True), but self.hit_element is None'

        # If the ray has hit an element, then destroy the element
        LOGGER.log_debug(f'Bullet hit element {self.hit_element.name}')
        LOGGER.log_debug(f'{self.hit_element.ray_destroyable=}')
        self.hit_element.destroy()

        # Inform global variables that the bullet will be destroyed
        if APP_VARS.last_bullet is self:
           APP_VARS.last_bullet = None 
        return super()._on_raycast_stopped(hit)