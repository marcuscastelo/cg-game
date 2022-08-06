
from dataclasses import dataclass
from dataclasses import dataclass, field
from utils.geometry import Vec3

from objects.element import PHYSICS_TPS

@dataclass
class Momentum:
    ''' Physics attribute that keeps track of the velocity of the element and provides methods to apply forces to it. '''
    velocity: Vec3 = field(default_factory=lambda: Vec3(0,0,0))
    accel: float = 0.01
    max_speed: float = 0.1

    # TODO: remover gambiarra de walk ter o y diferente
    def apply_force_walk(self, force: Vec3, delta_time: float):
        ''' Special case of apply_force for Player movement. '''
        y_vel = self.velocity.y + force.y * delta_time * PHYSICS_TPS * 0.01

        self.velocity += force * delta_time * PHYSICS_TPS * self.accel
        self.velocity.y = 0

        if self.velocity.magnitude() > self.max_speed:
            self.velocity = self.velocity.normalized() * self.max_speed

        self.velocity.y = y_vel
        pass

    def apply_force(self, force: Vec3, delta_time: float):
        ''' Applies a force to the element. '''
        self.velocity += force * delta_time * PHYSICS_TPS * self.accel
        if self.velocity.magnitude() > self.max_speed:
            self.velocity = self.velocity.normalized() * self.max_speed

    # TODO: friction is just a force, why have a separate method for it? (multiplicative factor)
    def apply_friction(self, percentage_keep: float, delta_time: float):
        ''' Applies friction to the element. '''
        self.velocity.xz *= 1 - ((1-percentage_keep) * delta_time * PHYSICS_TPS)
        # Example:
        # percentage = 0.99
        # delta_time = 1/50
        # 1 - (0.01 * 1/50 * 50) = 0.99