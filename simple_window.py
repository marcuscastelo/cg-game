import glfw
import OpenGL.GL as gl

def hsv_to_rgb(h, s, v):
    h = h / 60
    i = int(h)
    f = h - i
    p = v * (1 - s)
    q = v * (1 - s * f)
    t = v * (1 - s * (1 - f))

    if i == 0:
        return v, t, p
    elif i == 1:
        return q, v, p
    elif i == 2:
        return p, v, t
    elif i == 3:
        return p, q, v
    elif i == 4:
        return t, p, v
    else:
        return v, p, q


def main():
    glfw.init()

    window = glfw.create_window(640, 480, "Simple Window", monitor=None, share=None)
    glfw.make_context_current(window)
    glfw.show_window(window)

    hsv = [0.0, 1.0, 1.0]

    while not glfw.window_should_close(window):
        glfw.poll_events()
        
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

        gl.glClearColor(*hsv_to_rgb(*hsv), 1.0)
        hsv[0] = (hsv[0] + 0.5) % 360

        glfw.swap_buffers(window)

    glfw.terminate()

if __name__ == "__main__":
    main()