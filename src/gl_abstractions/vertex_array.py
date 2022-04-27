from OpenGL import GL as gl
from utils.logger import LOGGER

class VertexArray:
    def __init__(self):
        self.vao = gl.glGenVertexArrays(1)

    def bind(self):
        gl.glBindVertexArray(self.vao)

    def unbind(self):
        gl.glBindVertexArray(0)

    def __del__(self):
        LOGGER.log_warning(f'VertexArray(id={id(self)}) not deleted')
    #     gl.glDeleteVertexArrays(1, self.vao)