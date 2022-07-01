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
class SelectionRay(Ray):
    ''' A selection ray is a ray that can hit an element and select it. '''
    show_debug_cube: bool = False
    def __post_init__(self):
        if self.show_debug_cube:
            a = Cube('SelectionRayCube')
            self.transform.scale.xyz = Vec3(1,1,1) * 0.3

            self.shape_specs = a.shape_specs
        super().__post_init__()
    
    def on_spawned(self, world: 'World'):
        ''' Override of Element method. '''
        from app_vars import APP_VARS
        # Get a reference of world elements to be used in the raycast laters
        self.selectable_elements = world.elements
        return super().on_spawned(world)

    def _has_hit(self) -> bool:
        ''' Override of Ray method. '''

        # Filter out elements that are not selectable
        self.selectable_elements = [ element for element in self.selectable_elements if element.ray_selectable ]

        def calc_distance(element: Element) -> float:
            ''' Calculate the distance between the ray and the element. '''
            difference = element.center.xyz - self.center.xyz
            distance = difference.magnitude()
            return distance

        # Calculate the distance between the ray and each element
        distances = [ calc_distance(element) for element in self.selectable_elements ]

        # Sort the pairs by distance
        sorted_pairs = sorted(zip(distances, self.selectable_elements), key=lambda a: a[0])
        if sorted_pairs:
            # Get the element with the shortest distance
            element = sorted_pairs[0][1]
            distance = sorted_pairs[0][0]

            if distance < element.pseudo_hitbox_distance:
                # If the distance is less than the hitbox distance, then the ray has hit the element
                self.hit_element = element
                return True

        # If there are no pairs, then the ray has not hit anything
        self.hit_element = None
        return False

    def _on_raycast_stopped(self, hit: bool):
        ''' Override of Ray method. '''
        
        LOGGER.log_debug('SelectionRay Stopped!')
        from app_vars import APP_VARS

        if not hit:
            # If the ray has not hit anything, then destroy the bullet
            # FIXME: super() is not called!!! (this is a bug, probably)
            return
        
        assert self.hit_element, f'{hit=} (True), but self.hit_element is None'

        LOGGER.log_debug(f'Selection Hit element {self.hit_element.name}')

        # If the hit element is already the selected element, then ignore the hit
        if self.hit_element is APP_VARS.selected_element:
            pass
        else: # Otherwise, select the element
            if APP_VARS.selected_element:
                # If there is already a selected element, then deselect it
                APP_VARS.selected_element.unselect()
            # Select the hit element
            APP_VARS.selected_element = self.hit_element
            APP_VARS.selected_element.select()

        return super()._on_raycast_stopped(hit)