from cgitb import text
from dataclasses import dataclass, field
import os
import numpy as np
from OpenGL import GL as gl
from utils.geometry import Vec3
from app_vars import APP_VARS
from gl_abstractions.shader import Shader, ShaderDB
from gl_abstractions.texture import Texture, Texture2D
from objects.cube import Cube
from objects.element import Element, ElementSpecification, ShapeSpec
from utils.sig import metsig

from transform import Transform
from objects.wavefront import Model, RawVertex, WaveFrontReader

DEFAULT_MODEL = WaveFrontReader().load_model_from_file('./src/objects/cube.obj')

@dataclass
class LightCube(Cube):

    def _physics_update(self, delta_time: float):

        camera = APP_VARS.camera
        self.
        



        return super()._physics_update(delta_time)

