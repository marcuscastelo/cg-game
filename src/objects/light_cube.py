from cgitb import text
from dataclasses import dataclass, field
from dis import dis
import os
import random
import numpy as np
from OpenGL import GL as gl
from utils.geometry import Vec3
from gl_abstractions.shader import Shader, ShaderDB
from gl_abstractions.texture import Texture, Texture2D
from objects.cube import Cube
from objects.element import Element, ElementSpecification, ShapeSpec
from utils.sig import metsig

from transform import Transform
from wavefront.reader import WaveFrontReader

DEFAULT_MODEL = WaveFrontReader().load_model_from_file('models/cube.obj')

@dataclass
class LightCube(Cube):
    def __post_init__(self):
        from objects.physics.momentum import Momentum
        self._momentum = Momentum(accel=0.5, max_speed=3.5)
        return super().__post_init__()

    def _physics_update(self, delta_time: float):
        from app_vars import APP_VARS
        camera = APP_VARS.camera

        dist = camera.transform.translation - self.transform.translation
        force: Vec3 = dist.normalized()
        force += Vec3((random.random() * 2 - 1)/2, (random.random() * 2 - 1)/2, (random.random() * 2 - 1)/2)
        if dist.magnitude() < 1:
            if force.x > force.z:
                force.z = 1
            else:
                force.x = 1
        force.y = 0
        
        self._momentum.apply_force(force, delta_time=delta_time)
        self._momentum.apply_friction(0.9, delta_time=delta_time)
        self.transform.translation += self._momentum.velocity * delta_time
        # self.transform.translation += force * delta_time
        



        return super()._physics_update(delta_time)

