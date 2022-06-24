from dataclasses import dataclass
from gl_abstractions.shader import ShaderDB
from gl_abstractions.texture import Texture2D
from objects.element import Element, ShapeSpec

from OpenGL import GL as gl
import numpy as np

@dataclass
class Line(Element):
    shape_specs: list[ShapeSpec] = None

    def __post_init__(self):
        self.shape_specs = [
            ShapeSpec(
                vertices=np.array([
                    [*(0.0,0.0,0.0), ],#*(0.0, 0.0), *(0.0, 1.0, 0.0)],
                    [*(0.0,0.0,1.0), ],#*(1.0, 1.0), *(0.0, 1.0, 0.0)],
                ], dtype=np.float32),
                name='Line',
                render_mode=gl.GL_LINES,
                shader=ShaderDB.get_instance().get_shader('simple_red'),
            )
        ]

        return super().__post_init__()