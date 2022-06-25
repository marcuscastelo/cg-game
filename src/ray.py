from dataclasses import dataclass, field

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
        self.transform.translation.xyz += self.direction * delta_time * PHYSICS_TPS

        from app_vars import APP_VARS
        for element in APP_VARS.world.elements:
            if element in [APP_VARS.camera, self, APP_VARS.camera.raycast_line_dbg]:
                continue
            
            if element.name in ['Ground', 'light_cube']:
                continue

            difference = element.transform.translation.xyz - self.transform.translation.xyz
            scaled_difference = difference * element.transform.scale.xyz
            if element._state.selected:
                scaled_difference /= 2 # FIXME: hardcoded value

            distance = scaled_difference.magnitude()


            if distance < 1:
                LOGGER.log_debug(f'Selecting {element=}')
                element.select()
                # TODO: change behaviour VV
                self.direction = Vec3(0,0,0)
                self.transform.translation.xyz = Vec3(0,2,0)
                ## 
                break
            else:
                if element._state.selected:
                    element.destroy()
                    element.unselect()
        return super()._physics_update(delta_time)