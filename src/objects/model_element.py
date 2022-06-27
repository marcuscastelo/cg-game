from cgitb import text
from dataclasses import dataclass, field
import os
from re import M
import time
import numpy as np
from OpenGL import GL as gl
from utils.geometry import Vec3
from utils.logger import LOGGER
from gl_abstractions.shader import Shader, ShaderDB
from gl_abstractions.texture import Texture, Texture2D
from objects.element import Element, ElementSpecification, ShapeSpec
from utils.sig import metsig

from transform import Transform
from wavefront.reader import ModelReader
from wavefront.model import Model

@dataclass
class ModelElement(Element):
    model: Model = None
    shader: Shader = None
    texture: Texture = None
    shape_specs: list[ShapeSpec] = None

    def __post_init__(self):
        assert self.model, f'model field is required, got {self.model}'
        elspec = ElementSpecification.from_model(
            model=self.model,
            shader=self.shader,
            texture=self.texture,
        )
        self.shape_specs = elspec.shape_specs
        return super().__post_init__()

    def _physics_update(self, delta_time: float):
        return super()._physics_update(delta_time)
