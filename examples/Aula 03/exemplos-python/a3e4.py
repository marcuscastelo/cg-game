"""Estrela (triângulos)"""
import glfw
from OpenGL.GL import *
import numpy as np
# %%
glfw.init()
glfw.window_hint(glfw.VISIBLE, glfw.FALSE)
window = glfw.create_window(600, 600, "Triângulos", None, None)
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
PP = 2*np.pi/5
vertices = np.zeros(12, [("position", np.float32, 2)])
vertices['position'] = [(np.cos(PP/4), np.sin(PP/4)),
                        (np.cos((3/4)*PP)/3, np.sin((3/4)*PP)/3),
                        (np.cos((9/4)*PP), np.sin((9/4)*PP)),
                        (np.cos((11/4)*PP)/3, np.sin((11/4)*PP)/3),
                        (np.cos((17/4)*PP), np.sin((17/4)*PP)),
                        (np.cos((19/4)*PP)/3, np.sin((19/4)*PP)/3),
                        (np.cos((5/4)*PP), np.sin((5/4)*PP)),
                        (np.cos((7/4)*PP)/3, np.sin((7/4)*PP)/3),
                        (np.cos((13/4)*PP), np.sin((13/4)*PP)),
                        (np.cos((15/4)*PP)/3, np.sin((15/4)*PP)/3),
                        (np.cos(PP/4), np.sin(PP/4)),
                        (np.cos((3/4)*PP)/3, np.sin((3/4)*PP)/3)]
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
    glDrawArrays(GL_TRIANGLE_STRIP, 0, len(vertices))
    glfw.swap_buffers(window)
glfw.terminate()
