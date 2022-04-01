"""Cores"""
import glfw
from OpenGL.GL import *
import numpy as np
# %%
glfw.init()
glfw.window_hint(glfw.VISIBLE, glfw.FALSE)
window = glfw.create_window(720, 600, "Cores", None, None)
glfw.make_context_current(window)
VERTEX_CODE = """
        attribute vec2 position;
        void main(){
            gl_Position = vec4(position,0.0,1.0);
        }
        """
FRAGMENT_CODE = """
        uniform vec4 color;
        void main(){
            gl_FragColor = color;
        }
        """
program = glCreateProgram()
vertex = glCreateShader(GL_VERTEX_SHADER)
fragment = glCreateShader(GL_FRAGMENT_SHADER)
glShaderSource(vertex, VERTEX_CODE)
glShaderSource(fragment, FRAGMENT_CODE)
glCompileShader(vertex)
if not glGetShaderiv(vertex, GL_COMPILE_STATUS):
    error = glGetShaderInfoLog(vertex).decode()
    print(error)
    raise RuntimeError("Erro de compilacao do Vertex Shader")
glCompileShader(fragment)
if not glGetShaderiv(fragment, GL_COMPILE_STATUS):
    error = glGetShaderInfoLog(fragment).decode()
    print(error)
    raise RuntimeError("Erro de compilacao do Fragment Shader")
glAttachShader(program, vertex)
glAttachShader(program, fragment)
glLinkProgram(program)
if not glGetProgramiv(program, GL_LINK_STATUS):
    print(glGetProgramInfoLog(program))
    raise RuntimeError('Linking error')
glUseProgram(program)
vertices = np.zeros(3, [("position", np.float32, 2)])
vertices['position'] = [(.0, .0), (.5, .5), (.5, .0)]
buffer = glGenBuffers(1)
glBindBuffer(GL_ARRAY_BUFFER, buffer)
buffer = glGenBuffers(1)
glBindBuffer(GL_ARRAY_BUFFER, buffer)
glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_DYNAMIC_DRAW)
glBindBuffer(GL_ARRAY_BUFFER, buffer)
stride = vertices.strides[0]
offset = ctypes.c_void_p(0)
loc = glGetAttribLocation(program, "position")
glEnableVertexAttribArray(loc)
glVertexAttribPointer(loc, 2, GL_FLOAT, False, stride, offset)
loc_color = glGetUniformLocation(program, "color")
R = 1.0
G = 0.0
B = 0.0
glfw.show_window(window)
while not glfw.window_should_close(window):
    glfw.poll_events()
    glClear(GL_COLOR_BUFFER_BIT)
    glClearColor(1.0, 1.0, 1.0, 1.0)
    A = R
    R = G
    G = B
    B = A
    glUniform4f(loc_color, R, G, B, 1.0)
    glDrawArrays(GL_TRIANGLES, 0, len(vertices))
    glfw.swap_buffers(window)
glfw.terminate()
