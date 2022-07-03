from dataclasses import dataclass, field
import random
import time
from typing import Callable
from utils.geometry import Vec3
from objects.element import Element, ElementSpecification, ShapeSpec
from objects.cube import CUBE_MODEL
from wavefront.material import Material


@dataclass
class SpawnerRegion:
    ''' A region in which the spawner can spawn objects. '''
    start: Vec3
    end: Vec3


@dataclass
class SpawningProperties:
    ''' Properties of the spawning. '''
    # A random number generator that is used to generate the interval.
    min_interval: float = 0.5
    max_interval: float = 1.5

    # The maximum number of elements that can be alive at the same time.
    spawn_cap: int = 5

    # Whether the spawner should replace destroyed elements immediately or use the random interval.
    insta_replace_destroyed: bool = False


@dataclass
class Spawner(Element):
    ''' An element that spawns other elements within a region periodically. '''

    region: SpawnerRegion = None
    element_factory: Callable[[], Element] = None
    spawning_properties: SpawningProperties = field(
        default_factory=SpawningProperties)
    shape_specs: list[ShapeSpec] = None
    show_debug_cube: bool = False
    ray_destroyable: bool = False
    ray_selectable: bool = False

    def __post_init__(self):
        assert self.region, f"A region must be specified for the spawner {self.name}, got {self.region}"
        assert self.element_factory, f"An element factory must be specified for the spawner {self.name}, got {self.element_factory}"

        # If show_debug_cube is True, then there will be a cube that is used to show the region of the spawner.
        # TODO: GUI debug_options to show all spawner regions.
        if self.show_debug_cube:
            self.shape_specs = ElementSpecification.from_model(
                CUBE_MODEL).shape_specs  # TODO: self.elspec instead of shapespecs
            color = Vec3(0, 0, 0.3)  # Blue
            self.shape_specs[0].material = Material(
                'Transparent Spawner Overlay', Ka=color.xyz, Kd=color.xyz, d=0.1)
        else:
            self.shape_specs = []

        # Calculate the spawner position and scale based on the region.
        self.transform.scale.xyz = self.region.end - self.region.start
        self.transform.scale.x = max(abs(self.transform.scale.x), 1)
        self.transform.scale.y = max(abs(self.transform.scale.y), 1)
        self.transform.scale.z = max(abs(self.transform.scale.z), 1)

        self.transform.translation.xyz = (
            self.region.end.xyz + self.region.start.xyz) / 2
        self.transform.translation.y = self.region.start.y
        ###

        # Keeps track of all spawned elements.
        self.spawned_elements: list[Element] = []

        # Keeps track of the last time the spawner tried to spawn an element.
        # This is used to calculate the wait time.
        # Initialize with the current time (so that the spawner will not spawn immediately).
        self._last_tried_spawn_time = time.time()

        # Keeps track of the maximum number of concurrently spawned elements (used for insta_replace_destroyed).
        self._max_seen_elements = 0

        # Calculate the wait time.
        self._update_wait_time()

        return super().__post_init__()

    def _update_wait_time(self):
        ''' Calculates the wait time based on the spawning properties. '''
        min, max = self.spawning_properties.min_interval, self.spawning_properties.max_interval
        self._wait_time = random.uniform(min, max)

    def _remove_destroyed_elements(self):
        ''' Removes all destroyed elements from the spawned elements list. '''
        self.spawned_elements = [
            e for e in self.spawned_elements if not e.destroyed]

    def _spawn_element(self):
        ''' Spawns an element in a random position within the region. '''

        # Calculate the position of the element.
        pos = Vec3(
            random.uniform(self.region.start.x, self.region.end.x),
            random.uniform(self.region.start.y, self.region.end.y),
            random.uniform(self.region.start.z, self.region.end.z)
        )

        # Create the element.
        element = self.element_factory()
        element.transform.translation.xyz = pos

        # Add the element to the spawned elements list.
        from app_vars import APP_VARS
        # TODO: gain access to world in some other form
        APP_VARS.world.spawn(element)
        self.spawned_elements.append(element)

        # Update the maximum number of spawned elements.
        cur_element_count = len(self.spawned_elements)
        if cur_element_count > self._max_seen_elements:
            self._max_seen_elements = cur_element_count

    def _physics_update(self, delta_time: float):
        ''' Updates the spawner. '''

        # Remove all destroyed elements.
        self._remove_destroyed_elements()

        # Calculate the time since the last time the spawner tried to spawn an element.
        elapsed_time = time.time() - self._last_tried_spawn_time

        # If the elapsed time is greater than the wait time, then try to spawn an element.
        if elapsed_time > self._wait_time:
            self._last_tried_spawn_time = time.time()

            # If the maximum number of spawned elements is not reached, then spawn an element.
            element_count = len(self.spawned_elements)
            has_room_for_spawn = element_count < self.spawning_properties.spawn_cap
            if has_room_for_spawn:
                self._spawn_element()

            # Update the wait time, even if the spawner didn't spawn an element.
            self._update_wait_time()

        # If the insta_replace_destroyed property is set, then replace destroyed elements immediately.
        if self.spawning_properties.insta_replace_destroyed:
            # Calculate the number of elements that have been destroyed.
            element_count = len(self.spawned_elements)
            missing_element_count = self._max_seen_elements - element_count

            if missing_element_count > 0:
                # Spawn missing elements.
                for _ in range(missing_element_count):
                    self._spawn_element()

        return super()._physics_update(delta_time)
