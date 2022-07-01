from dataclasses import dataclass
import math
import random
import time

from utils.geometry import Vec3
from objects.model_element import ModelElement
from objects.physics.rotation import front_to_rotation
from wavefront.model import Model
from wavefront.model_reader import ModelReader


BOT_MODEL = ModelReader().load_model_from_file('models/bot.obj')

@dataclass
class Bot(ModelElement):
    ''' Enemy bot that wanders around the world '''
    model: Model = BOT_MODEL
    ray_destroyable: bool = True # The player can shoot the bot
    ray_selectable: bool = True # For debugging purposes

    def __post_init__(self):
        from objects.physics.momentum import Momentum
        self._dying = False # Used to animate the bot dying
        self.momentum = Momentum() # Physics momentum (velocity and force)

        # Define the amplitude of the movement in the x and z axis
        self.amp_x = random.uniform(0.3, 1.7)
        self.amp_z = random.uniform(0.3, 1.7)
        self.per_x = random.uniform(0.3, 1.7)
        self.per_z = random.uniform(0.3, 1.7)
        return super().__post_init__()

    @property
    def center(self) -> Vec3:
        ''' Override of Element property. '''
        return self.transform.translation + Vec3(0, 0.5, 0) * self.transform.scale

    @property
    def pseudo_hitbox_distance(self) -> float:
        ''' Override of Element property. '''
        return super().pseudo_hitbox_distance * 0.5

    def update(self, delta_time: float):
        ''' Override of Element method. '''
        # Check if the bot is dying (hit by a bullet or marked to be destroyed by some means)
        if self._dying:
            # Animate scaling down the bot until it becomes too small
            self.transform.scale *= 1 - (0.06 * delta_time * 60)
            if self.transform.scale.magnitude() < 0.01:
                # Then, actually destroy the bot
                super().destroy()

        return super().update(delta_time)

    def _physics_update(self, delta_time: float):
        ''' Override the method of the Element class. '''
        from constants import WORLD_SIZE

        # Move the bot according to its momentum
        # But only if it's not dying
        if not self._dying:
            self.momentum.apply_force(Vec3(math.sin(time.time() * self.per_x) * self.amp_x, 0, math.cos(time.time() * self.per_z) * self.amp_z), delta_time=delta_time)
            self.transform.translation += self.momentum.velocity 
            
            if self.transform.translation.x < -WORLD_SIZE/2 or self.transform.translation.x > WORLD_SIZE/2:
                self.momentum.velocity.x *= -1
                self.per_x += math.pi
            if self.transform.translation.z < 0 or self.transform.translation.z > WORLD_SIZE/2:
                self.momentum.velocity.z *= -1
                self.per_z += math.pi
            self.transform.rotation.xyz = front_to_rotation(self.momentum.velocity)
            self.transform.rotation.y -= math.pi/2
        
        return super()._physics_update(delta_time)

    def destroy(self):
        ''' Override of Element method. '''
        # Instead of immediately destroying the bot, mark it as dying for the animation to start
        print('Destroy!')
        self._dying = True