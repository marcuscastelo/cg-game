import time
import glfw
import OpenGL.GL as gl

def setup():
    glfw.init()
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    window = glfw.create_window(640, 480, "Simple Window", monitor=None, share=None)
    glfw.make_context_current(window)
    glfw.show_window(window)

    # Create a vertex array object
    vao = gl.glGenVertexArrays(1)

    # Create a vertex buffer object
    vbo = gl.glGenBuffers(1)

    # Bind the Vertex Array Object first, then bind and set vertex buffer(s) and attribute pointer(s).
    gl.glBindVertexArray(vao)
    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo)

    # Set the vertex buffer data
    vertices = [
        0.0,  0.5, 0.0,
        0.5, -0.5, 0.0,
        -0.5, -0.5, 0.0
    ]
    gl.glBufferData(gl.GL_ARRAY_BUFFER, len(vertices)*4, (gl.GLfloat * len(vertices))(*vertices), gl.GL_STATIC_DRAW)

    # Specify the layout of the vertex data
    gl.glEnableVertexAttribArray(0)
    gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, gl.GL_FALSE, 0, None)

def draw():
    gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
    
    gl.glBindVertexArray(1)    

    # Draw the triangle
    gl.glDrawArrays(gl.GL_TRIANGLES, 0, 3)

    # Unbind the buffer when we're done
    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)
    gl.glBindVertexArray(0)

def finish():
    glfw.terminate()

def main():
    setup()
    while not glfw.window_should_close(glfw.get_current_context()):
        glfw.poll_events()
        draw()
        glfw.swap_buffers(glfw.get_current_context())
    finish()

if __name__ == "__main__":
    main()