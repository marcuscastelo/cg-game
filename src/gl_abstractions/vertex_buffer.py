from OpenGL import GL as gl

import numpy as np
from utils.logger import LOGGER

from gl_abstractions.layout import Layout

class VertexBuffer:
    def __init__(self, layout: Layout, data: np.ndarray, usage: int = gl.GL_STATIC_DRAW):
        self.vbo = gl.glGenBuffers(1)
        self.data = data
        self.layout = layout

        layout.assert_data_ok(data)
        # Data is a 2D array of floats.
        # The first dimension is the attribute, the second dimension is the attribute's values.

        
        # TODO: SUPPORTED_DTYPES = [np.float32, np.float64] (layout.py): make them share behaviour
        assert data.dtype == np.float32, f'Only float32 data is supported, got {data.dtype}'
        flattened_data = data.flatten()

        FloatVec = gl.GLfloat * len(flattened_data)
        data_ptr = FloatVec(*flattened_data)
        data_ptr_size = len(flattened_data) * 4

        self.bind()
        gl.glBufferData(gl.GL_ARRAY_BUFFER, flattened_data.nbytes, data_ptr, usage)
        self.unbind()

    def bind(self):
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.vbo)

    def unbind(self):
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)

    def __del__(self):
        # gl.glDeleteBuffers(1, [self.vbo])
        # LOGGER.log_warning(f'VertexBuffer(id={id(self)}) not deleted') # TODO: cleanup
        pass