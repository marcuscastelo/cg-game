from cgitb import text
from dataclasses import dataclass, field
from dis import dis
import math
import os
import random
import time
import glm
import numpy as np
from OpenGL import GL as gl
from utils.geometry import Vec3
from gl_abstractions.shader import Shader, ShaderDB
from gl_abstractions.texture import Texture, Texture2D
from objects.model_element import ModelElement
from objects.element import Element, ElementSpecification, ShapeSpec
from utils.sig import metsig
from objects.physics.rotation import front_to_rotation
from wavefront.model import Model

from wavefront.model_reader import ModelReader

MODEL = ModelReader().load_model_from_file('models/aux_robot.obj')

@dataclass
class AuxRobot(ModelElement):
    model: Model = MODEL
    ray_selectable: bool = False
    ray_destroyable: bool = False
    def __post_init__(self):
        from objects.physics.momentum import Momentum
        self._momentum = Momentum(accel=0.5, max_speed=3.5)
        super().__post_init__()

    def update(self, delta_time: float):
        from app_vars import APP_VARS
        APP_VARS.lighting_config.light_position = self.transform.translation
        return super().update(delta_time)

    def _physics_update(self, delta_time: float):
        from app_vars import APP_VARS
        import constants

        look_target = APP_VARS.camera if APP_VARS.last_bullet is None or (APP_VARS.last_bullet.center - APP_VARS.camera.center).magnitude() > constants.WORLD_SIZE else APP_VARS.last_bullet
        follow_target = APP_VARS.camera

        dist = follow_target.transform.translation - self.transform.translation

        if dist.magnitude() > constants.WORLD_SIZE:
            self.transform.translation.xyz = follow_target.transform.translation.xyz

        force: Vec3 = dist.normalized()
        # force += Vec3((random.random() * 2 - 1)/2, (random.random() * 2 - 1)/2, (random.random() * 2 - 1)/2)
        if dist.magnitude() < 3:
            force.x = force.z = 0
        force.y = 0
        
        self._momentum.apply_force(force, delta_time=delta_time)
        self._momentum.apply_friction(0.9, delta_time=delta_time)
        self.transform.translation += self._momentum.velocity * delta_time
        # self.transform.translation += force * delta_time
        target_rotation = front_to_rotation(look_target.transform.translation - self.transform.translation)
        target_rotation.y -= math.pi/2

        # Delta rotation is the difference between the target rotation and the current rotation
        delta_rot = target_rotation - self.transform.rotation
        # Check if the delta rotation should be inverted
        if delta_rot.y > math.pi:
            delta_rot.y -= 2 * math.pi
        elif delta_rot.y < -math.pi:
            delta_rot.y += 2 * math.pi
        # Apply the delta rotation

        self.transform.rotation += delta_rot * delta_time * 2

        self.transform.translation.y = (math.sin(time.time() / 2) / 2 + 1) * (2 - 1.8) + 1.8


        return super()._physics_update(delta_time)

