from dataclasses import dataclass
from threading import Thread
from dpgext import gui
from dpgext import elements as el
from dpgext.utils.sig import metsig
from dpgext.utils.logger import LOGGER

import glfw
import OpenGL.GL as gl
import numpy as np

from threading import Thread

import dearpygui.dearpygui as dpg

@dataclass
class AppState:
    scale: float = 1.0

STATE = AppState()

class MainWindow(gui.Window):
    @metsig(gui.Window.__init__)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def describe(self):
        with self:
            el.Text("Hello World!").construct()
            el.Slider(STATE, 'scale').construct(width=200, height=20)

class AppGui(gui.Gui):
    def _init_windows(self):
        self.windows['main'] = MainWindow()
        return super()._init_windows()


def create_window():
    glfw.init()
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    window = glfw.create_window(640, 480, "Simple Window", monitor=None, share=None)
    glfw.make_context_current(window)
    glfw.show_window(window)
    return window

def glfw_thread():
    window = create_window()

    vao = gl.glGenVertexArrays(1)
    vbo = gl.glGenBuffers(1)

    gl.glBindVertexArray(vao)
    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo)

    vertices = [
        0.0,  0.5, 0.0,
        0.5, -0.5, 0.0,
        -0.5, -0.5, 0.0
    ]
    # Set the vertex buffer data
    gl.glBufferData(gl.GL_ARRAY_BUFFER, len(vertices)*4, (gl.GLfloat * len(vertices))(*vertices), gl.GL_STATIC_DRAW)

    gl.glEnableVertexAttribArray(0)
    gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, gl.GL_FALSE, 0, None)

    while not glfw.window_should_close(window):
        glfw.poll_events()

        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        gl.glClearColor(1.0, 1.0, 1.0, 1.0)

        gl.glBindVertexArray(vao)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo)

        # Draw the triangle
        gl.glColor3f(1.0, 0.0, 0.0)
        gl.glDrawArrays(gl.GL_TRIANGLES, 0, 3)


        glfw.swap_buffers(glfw.get_current_context())

def main():
    glfw.init()
    gui = AppGui()

    t = Thread(target=glfw_thread)
    t.start()
    gui.run()

    t.join()


    glfw.terminate()
if __name__ == "__main__":
    main()