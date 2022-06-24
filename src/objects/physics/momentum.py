
from dataclasses import dataclass
from dataclasses import dataclass, field
from itertools import accumulate
import math
from turtle import shape
import glm
from utils.geometry import Vec3
from utils.sig import metsig
import constants
import glfw

from objects.element import PHYSICS_TPS, Element, ElementSpecification, ShapeSpec
from objects.world import World
from transform import Transform

from input.input_system import INPUT_SYSTEM as IS

@dataclass
class Momentum:
    velocity: Vec3 = field(default_factory=lambda: Vec3(0,0,0))
    accel: float = 0.01
    max_speed: float = 0.1

    # TODO: remover gambiarra de walk ter o y diferente
    def apply_force_walk(self, force: Vec3, delta_time: float):
        y_vel = self.velocity.y + force.y * delta_time * PHYSICS_TPS * 0.01

        self.velocity += force * delta_time * PHYSICS_TPS * self.accel
        self.velocity.y = 0

        if self.velocity.magnitude() > self.max_speed:
            self.velocity = self.velocity.normalized() * self.max_speed

        self.velocity.y = y_vel
        pass

    def apply_force(self, force: Vec3, delta_time: float):
        self.velocity += force * delta_time * PHYSICS_TPS * self.accel
        if self.velocity.magnitude() > self.max_speed:
            self.velocity = self.velocity.normalized() * self.max_speed


    def apply_friction(self, percentage: float, delta_time: float):
        self.velocity.xz *= percentage