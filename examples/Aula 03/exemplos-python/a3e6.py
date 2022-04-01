"""Círculos"""
import glfw
from OpenGL.GL import *
import numpy as np
# %%
glfw.init()
glfw.window_hint(glfw.VISIBLE, glfw.FALSE)
width = 800
height = 500
window = glfw.create_window(width, height, "Círculos", None, None)
glfw.make_context_current(window)
VERTEX_CODE = """
        attribute vec2 position;
        void main(){
            gl_Position = vec4(position,0.0,1.0);
        }
        """
FRAGMENT_CODE = """
        void main(){
            gl_FragColor = vec4(0.0, 0.0, 0.0, 1.0);
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
num_vertices = 64
counter = 0
radius = .5
vertices = np.zeros(num_vertices, [("position", np.float32, 2)])
angle = 0.0
center = [.25, .25]
ratio = width/height
for counter in range(num_vertices):
    angle += 2*np.pi/num_vertices
    x = np.cos(angle)*radius/ratio
    y = np.sin(angle)*radius
    vertices[counter] = [x+center[0], y+center[1]]
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
glfw.show_window(window)
while not glfw.window_should_close(window):
    glfw.poll_events()
    glClear(GL_COLOR_BUFFER_BIT)
    glClearColor(1.0, 1.0, 1.0, 1.0)
    glDrawArrays(GL_TRIANGLE_FAN, 0, len(vertices))
    glfw.swap_buffers(window)
glfw.terminate()
