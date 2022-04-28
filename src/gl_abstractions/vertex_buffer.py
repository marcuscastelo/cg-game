from OpenGL import GL as gl

import numpy as np
from utils.logger import LOGGER

class VertexBuffer:
    def __init__(self, data: np.ndarray, usage: int = gl.GL_STATIC_DRAW):
        self.vbo = gl.glGenBuffers(1)
        self.data = data

        assert data.dtype == np.float32, f'Only float32 data is supported, got {data.dtype}'

        FloatVec = gl.GLfloat * len(data)
        data_ptr = FloatVec(*data)
        data_ptr_size = len(data) * 4

        self.bind()
        gl.glBufferData(gl.GL_ARRAY_BUFFER, data.nbytes, data_ptr, usage)
        self.unbind()

    def bind(self):
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.vbo)

    def unbind(self):
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)

    def __del__(self):
        # gl.glDeleteBuffers(1, [self.vbo])
        # LOGGER.log_warning(f'VertexBuffer(id={id(self)}) not deleted') # TODO: cleanup
        pass