from cgitb import text
from dataclasses import dataclass, field
from dis import dis
import math
import os
import random
import glm
import numpy as np
from OpenGL import GL as gl
from utils.geometry import Vec3
from gl_abstractions.shader import Shader, ShaderDB
from gl_abstractions.texture import Texture, Texture2D
from objects.model_element import ModelElement
from objects.element import Element, ElementSpecification, ShapeSpec
from utils.sig import metsig

from transform import Transform
from wavefront.material import Material
from wavefront.reader import ModelReader

DEFAULT_MODEL = ModelReader().load_model_from_file('models/cube.obj')

@dataclass
class AuxRobot(ModelElement):
    def __post_init__(self):
        from objects.physics.momentum import Momentum
        self._momentum = Momentum(accel=0.5, max_speed=3.5)
        super().__post_init__()
        self.shape_specs[0].material = Material('lc')
        self.shape_specs[0].material.Ka.xyz = Vec3(1000,1000,1000)
        self.shape_specs[0].material.Kd.xyz = Vec3(1,0,0)

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

