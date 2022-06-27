from dataclasses import dataclass, field
import random
import time
from typing import Callable
from utils.geometry import Vec3
from utils.logger import LOGGER
from objects.element import Element, ElementSpecification, ShapeSpec
from objects.cube import CUBE_MODEL
from wavefront.material import Material

@dataclass
class SpawnerRegion:
    start: Vec3
    end: Vec3

@dataclass
class SpawningProperties:
    min_interval: float = 1
    max_interval: float = 3
    max_spawned_elements: int = 5

@dataclass
class Spawner(Element):
    region: SpawnerRegion = None
    element_factory: Callable[[], Element] = None
    spawning_properties: SpawningProperties = field(default_factory=SpawningProperties)
    shape_specs: list[ShapeSpec] = None
    show_debug_cube: bool = False

    def __post_init__(self):
        assert self.region, f"region must be provided, got {self.region}"
        assert self.element_factory, f"region must be provided, got {self.element_factory}"
        if self.show_debug_cube:
            self.shape_specs = ElementSpecification.from_model(CUBE_MODEL).shape_specs # TODO: self.elspec instead of shapespecs
            color = Vec3(0,0,0.3) # Blue
            self.shape_specs[0].material = Material('Transparent Spawner Overlay', Ka=color.xyz, Kd=color.xyz, d=0.1)
        else:
            self.shape_specs = []
            
        self.transform.scale.xyz = self.region.end - self.region.start
        self.transform.scale.x = max(abs(self.transform.scale.x), 1)
        self.transform.scale.y = max(abs(self.transform.scale.y), 1)
        self.transform.scale.z = max(abs(self.transform.scale.z), 1)

        self.transform.translation.xyz = (self.region.end.xyz + self.region.start.xyz) / 2
        self.transform.translation.y = self.region.start.y

        self.spawned_elements: list[Element] = []
        self._last_tried_spawn_time = time.time() # Pretend it has already spawned (to avoid instant spawns)
        self._update_wait_time()
        return super().__post_init__()

    def _update_wait_time(self):
        self._wait_time = random.random() * (self.spawning_properties.max_interval - self.spawning_properties.min_interval) + self.spawning_properties.min_interval

    def _remove_destroyed_elements(self):
        self.spawned_elements = [ element for element in self.spawned_elements if not element.destroyed ]

    def _spawn_element(self):
        good_position = False
        while not good_position:
            random_vec = Vec3(random.random(),random.random(),random.random())
            random_pos = self.region.start + random_vec * (self.region.end - self.region.start)

            good_position = True
            for new_element in self.spawned_elements:
                if (new_element.transform.translation - random_pos).magnitude() < 1:
                    good_position = False
                    break

        from app_vars import APP_VARS
        new_element = self.element_factory()
        new_element.transform.translation.xyz = random_pos

        APP_VARS.world.spawn(new_element) # TODO: gain access to world in some other form
        self.spawned_elements.append(new_element)
        pass

    def _physics_update(self, delta_time: float):
        elapsed_time = time.time() - self._last_tried_spawn_time
        if elapsed_time > self._wait_time:
            self._remove_destroyed_elements()
            
            self._last_tried_spawn_time = time.time()
            if len(self.spawned_elements) < self.spawning_properties.max_spawned_elements:
                LOGGER.log_debug(f'Spawned after {self._wait_time}!')
                self._spawn_element()
            else:
                LOGGER.log_debug(f'Spawner maximum capacity reached {len(self.spawned_elements)}/{self.spawning_properties.max_spawned_elements}')
            self._update_wait_time()


        return super()._physics_update(delta_time)