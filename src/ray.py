from dataclasses import dataclass, field
from dis import dis

from utils.geometry import Vec3
from utils.logger import LOGGER
from objects.element import PHYSICS_TPS, Element, ShapeSpec
from objects.cube import Cube

@dataclass
class Ray(Element):
    direction: Vec3 = field(default_factory=lambda: Vec3(0,0,0))
    shape_specs: list[ShapeSpec] = None

    def __post_init__(self):
        a = Cube('test_cube')
        self.transform.scale.xyz = Vec3(1,1,1) * 0.3

        self.shape_specs = a.shape_specs
        super().__post_init__()

    def _physics_update(self, delta_time: float):
        self.transform.translation.xyz += self.direction * delta_time * PHYSICS_TPS * 0.3

        from app_vars import APP_VARS

        selectable_elements = APP_VARS.world.elements
        selectable_elements = [ element for element in selectable_elements if element not in [APP_VARS.camera, self, APP_VARS.camera.raycast_line_dbg] ]
        selectable_elements = [ element for element in selectable_elements if element.name not in ['Ground', 'light_cube'] ]

        def calc_distance(element: Element) -> float:
            difference = element.transform.translation.xyz - self.transform.translation.xyz
            scaled_difference = difference * element.transform.scale.xyz
            # if element._state.selected:
            #     scaled_difference /= 2 # FIXME: hardcoded value

            distance = scaled_difference.magnitude()
            return distance

        distances = [ calc_distance(element) for element in selectable_elements ]

        def stop_raycast():
                self.direction = Vec3(0,0,0)
                self.transform.translation.xyz = Vec3(0,100,0)
                keep_iterating = False

        sorted_pairs = sorted(zip(distances, selectable_elements), key=lambda a: a[0])
        if sorted_pairs:
            element = sorted_pairs[0][1]
            distance = sorted_pairs[0][0]



            if distance < 1:
                if element._state.selected:
                    element.unselect()
                else:
                    element.select()
                
                stop_raycast()

        # for element in APP_VARS.world.elements:
        #     if element in [APP_VARS.camera, self, APP_VARS.camera.raycast_line_dbg]:
        #         continue
            
        #     if element.name in ['Ground', 'light_cube']:
        #         continue

        #     difference = element.transform.translation.xyz - self.transform.translation.xyz
        #     scaled_difference = difference * element.transform.scale.xyz
        #     if element._state.selected:
        #         scaled_difference /= 2 # FIXME: hardcoded value

        #     distance = scaled_difference.magnitude()

        #     DST = 1
        #     keep_iterating = True
        #     def stop_raycast():
        #         self.direction = Vec3(0,0,0)
        #         self.transform.translation.xyz = Vec3(0,100,0)
        #         keep_iterating = False

        #     if self.transform.translation.xyz.magnitude() > 30:
        #         stop_raycast()

        #     if distance < DST:
        #         if element._state.selected:
        #             element.unselect()
        #         else:
        #             element.select()
        #         stop_raycast()
        #     else:
        #         if element._state.selected:
        #             # element.destroy()
        #             # element.unselect()
        #             pass

        #     if not keep_iterating:
        #         break
        return super()._physics_update(delta_time)