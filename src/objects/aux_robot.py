from dataclasses import dataclass
import math
import time
from utils.geometry import Vec3
from objects.model_element import ModelElement
from objects.physics.rotation import front_to_rotation
from wavefront.model import Model

from wavefront.model_reader import ModelReader

AUX_ROBOT_MODEL = ModelReader().load_model_from_file('models/aux_robot.obj')

@dataclass
class AuxRobot(ModelElement):
    ''' 
    A little robot that follows and looks to the player. 
    When it gets close, it stops and just looks at the player, going up and down smoothly.
    When a bullet is fired, it looks at the bullet. 
    '''
    model: Model = AUX_ROBOT_MODEL
    ray_selectable: bool = False    # To avoid undesired selection of the aux robot, we disable its selection
    ray_destroyable: bool = False   # It is not destroyable by the player (because it's the player's best friend) 

    def __post_init__(self):
        from objects.physics.momentum import Momentum
        self._momentum = Momentum(accel=0.5, max_speed=3.5)
        super().__post_init__()

    def update(self, delta_time: float):
        ''' Override the method of the Element class. '''
        from app_vars import APP_VARS
        APP_VARS.lighting_config.light_position = self.transform.translation
        return super().update(delta_time)

    def _physics_update(self, delta_time: float):
        ''' Override the method of the Element class. '''
        from app_vars import APP_VARS
        import constants

        # 1. Determine targets #

        # Determine what the aux robot should look at
        look_target = APP_VARS.camera if APP_VARS.last_bullet is None or (APP_VARS.last_bullet.center - APP_VARS.camera.center).magnitude() > constants.WORLD_SIZE else APP_VARS.last_bullet
        # Determine what the aux robot should move to
        follow_target = APP_VARS.camera

        # 2. Move #

        # Calculate the aux robot's movement
        dist = follow_target.transform.translation - self.transform.translation

        if dist.magnitude() > constants.WORLD_SIZE:
            self.transform.translation.xyz = follow_target.transform.translation.xyz

        force: Vec3 = dist.normalized()
        # force += Vec3((random.random() * 2 - 1)/2, (random.random() * 2 - 1)/2, (random.random() * 2 - 1)/2)
        if dist.magnitude() < 3:
            force.x = force.z = 0
        force.y = 0 # Don't move up/down
        
        # Apply the force to the aux robot
        self._momentum.apply_force(force, delta_time=delta_time)
        # Also apply friction to the aux robot
        self._momentum.apply_friction(0.9, delta_time=delta_time)

        # Apply velocity to the aux robot transform
        self.transform.translation += self._momentum.velocity * delta_time

        # 3. Look #

        # Calculate the rotation to look at the target
        target_rotation = front_to_rotation(look_target.transform.translation - self.transform.translation)
        target_rotation.y -= math.pi/2 # Model (.obj) is rotated 90 degrees around the y axis
        delta_rot = target_rotation - self.transform.rotation

        # Determine which way the aux robot should turn to minimize rotation time
        if delta_rot.y > math.pi:
            delta_rot.y -= 2 * math.pi
        elif delta_rot.y < -math.pi:
            delta_rot.y += 2 * math.pi

        # Apply the delta rotation
        self.transform.rotation += delta_rot * delta_time * 2

        # 4. Animate up/down #
        self.transform.translation.y = (math.sin(time.time() / 2) / 2 + 1) * (2 - 1.8) + 1.8

        return super()._physics_update(delta_time)

