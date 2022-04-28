from OpenGL import GL as gl
from utils.logger import LOGGER

from gl_abstractions.layout import Layout

class VertexArray:
    def __init__(self):
        self.vao = gl.glGenVertexArrays(1)

    def bind(self):
        gl.glBindVertexArray(self.vao)

    def unbind(self):
        gl.glBindVertexArray(0)

    def apply_layout(self, layout: Layout):
        stride = layout.calc_stride()
        
        i = 0
        for name, count in layout.attributes:
            # LOGGER.log_trace(f'{name=}, {count=}')
            offset = layout.get_offset(name)
            gl.glEnableVertexAttribArray(i)
            gl.glVertexAttribPointer(i, count, gl.GL_FLOAT, gl.GL_FALSE, stride, offset)
            i += 1


    def __del__(self):
        # LOGGER.log_warning(f'VertexArray(id={id(self)}) not deleted') #TODO: cleanup
    #     gl.glDeleteVertexArrays(1, self.vao)
        pass