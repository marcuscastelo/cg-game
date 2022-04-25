from threading import Thread

import glfw
import OpenGL.GL as gl

from threading import Thread

from utils.logger import LOGGER

from constants import WINDOW_SIZE
from app_state import APP_VARS, OpenGLScene
from gui import AppGui

def create_window():
    glfw.init()

    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, gl.GL_TRUE)
    glfw.window_hint(glfw.RESIZABLE, gl.GL_FALSE)

    window = glfw.create_window(*WINDOW_SIZE, "CG Trab 1", monitor=None, share=None)

    glfw.make_context_current(window)
    glfw.show_window(window)
    return window

def glfw_thread():
    window = create_window()

    # Enable depth test
    gl.glEnable(gl.GL_DEPTH_TEST)
    gl.glDepthFunc(gl.GL_LESS)
    
    # Enable blending
    gl.glEnable(gl.GL_BLEND)
    gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)


    # fbo = gl.glGenFramebuffers(1)
    # gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, fbo)


    # # Color attachment
    # texture = gl.glGenTextures(gl.GL_TEXTURE_2D, 1)
    # gl.glBindTexture(gl.GL_TEXTURE_2D, texture)

    # gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
    # gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)
    # gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGBA8, *WINDOW_SIZE, 0, gl.GL_RGBA8, gl.GL_UNSIGNED_BYTE, None)

    # gl.glBindTexture(gl.GL_TEXTURE_2D, 0)

    # APP_VARS.scene = OpenGLScene(fbo, texture)
    # gl.glFramebufferTexture2D(gl.GL_FRAMEBUFFER, gl.GL_COLOR_ATTACHMENT0, gl.GL_TEXTURE_2D, APP_VARS.scene.texture, 0)

    # # Depth attachment
    # depth_texture = gl.glGenTextures(1)
    # gl.glBindTexture(gl.GL_TEXTURE_2D, depth_texture)
    # gl.glTextureStorage2D(depth_texture, 0, gl.GL_DEPTH24_STENCIL8, *WINDOW_SIZE)
    # gl.glFramebufferTexture2D(gl.GL_FRAMEBUFFER, gl.GL_DEPTH_STENCIL_ATTACHMENT, gl.GL_TEXTURE_2D, depth_texture, 0)


    # # TODO: try to reorder (first color, then depth and then generate framebuffer, etc. see https://docs.gl/gl4/glGenFramebuffers)

    # Check if framebuffer is complete
    status = gl.glCheckFramebufferStatus(gl.GL_FRAMEBUFFER)
    if status != gl.GL_FRAMEBUFFER_COMPLETE:
        LOGGER.log_error("Framebuffer is not complete", 'glfw_thread')
        glfw.terminate()
        return

    gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, 0)

    world = APP_VARS.world

    world.setup_scene() # Places the ship in the world and creates the enemies

    while not glfw.window_should_close(window) and not APP_VARS.closing:
        glfw.poll_events()

        def render():
            # gl.glUniformMatrix4fv(mvp_loc, 1, gl.GL_FALSE, STATE.mvp_manager.mvp)

            gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
            gl.glClearColor(1.0, 1.0, 1.0, 1.0)

            world.update()

        render()

        glfw.swap_buffers(glfw.get_current_context())
    
    LOGGER.log_info("GLFW thread is closing", 'glfw_thread')
    APP_VARS.closing = True


def _set_signal_handler():
    # Handle CTRL+C (SIGINT) signal
    def signal_handler(_signal, _frame):
        APP_VARS.closing = True

    import signal
    signal.signal(signal.SIGINT, signal_handler)


def main():
    _set_signal_handler()
    
    LOGGER.log_info("Starting app", 'main')

    LOGGER.log_trace("Init Glfw", 'main')
    glfw.init()
    
    LOGGER.log_trace("Init GUI", 'main')
    gui = AppGui()

    LOGGER.log_trace("Start GLFW thread", 'main')
    t = Thread(target=glfw_thread)
    t.start()

    # LOGGER.log_trace("Start GUI", 'main')
    # gui.run()

    LOGGER.log_info("GUI Has been closed, waiting for GLFW to close...", 'main')
    t.join()
    LOGGER.log_info("GLFW thread has been closed", 'main')

    LOGGER.log_trace("Terminating Glfw", 'main')
    glfw.terminate()
    LOGGER.log_info("App has been closed gracefully", 'main')

if __name__ == "__main__":
    main()

    # assert Rect2(Vec2(0, 0), Vec2(1, 1)) == Rect2(Vec2(0, 0), Vec2(1, 1))
    # assert Rect2(Vec2(0, 0), Vec2(1, 1)) != Rect2(Vec2(0, 0), Vec2(1, 2))
    # assert Rect2(Vec2(0, 0), Vec2(1, 1)) == Rect2(0, 0, 1, 1)
    # assert Rect2(Vec2(0, 0), Vec2(1, 1)) != Rect2(0, 0, 1, 2)
    # assert Rect2(Vec2(0, 0), Vec2(1, 1)) == Rect2(Vec2(0, 0), size=Vec2(1, 1))
    # assert Rect2(Vec2(0, 0), Vec2(1, 2)) == Rect2(Vec2(0, 0), width=1, height=2)
    # assert Rect2(Vec2(0, 0), Vec2(1, 1)) != Rect2(Vec2(0, 0), width=1, height=2)

    # assert Rect2(Vec2(10, 10), Vec2(20, 20)) == Rect2(10, 10, 20, 20)
    # assert Rect2(Vec2(10, 10), Vec2(20, 20)) != Rect2(10, 10, 20, 21)
    # assert Rect2(Vec2(10, 10), Vec2(20, 20)) == Rect2(Vec2(10, 10), Vec2(20, 20))
    # assert Rect2(Vec2(10, 10), Vec2(20, 20)) != Rect2(Vec2(10, 10), Vec2(20, 21))
    # assert Rect2(Vec2(10, 10), Vec2(20, 20)) == Rect2(10, 10, size=Vec2(10, 10))
    # assert Rect2(Vec2(10, 10), Vec2(20, 20)) != Rect2(10, 10, size=Vec2(10, 11))
    # assert Rect2(Vec2(10, 10), Vec2(20, 20)) == Rect2(Vec2(10, 10), width=10, height=10)
    # assert Rect2(Vec2(10, 10), Vec2(20, 20)) != Rect2(Vec2(10, 10), width=10, height=11)
    # assert Rect2(Vec2(10, 10), Vec2(20, 20)) == Rect2(Rect2(Vec2(10, 10), Vec2(20, 20)))

    # rect = Rect2(Vec2(10, 10), Vec2(20, 20))
    # assert rect.start == Vec2(10, 10)
    # assert rect.end == Vec2(20, 20)
    # assert rect.size == Vec2(10, 10)
    # assert rect.width == 10
    # assert rect.height == 10
    # assert rect.center == Vec2(15, 15)
    # assert rect.left == 10
    # assert rect.right == 20
    # assert rect.top == 20
    # assert rect.bottom == 10
    # assert rect.top_left == Vec2(10, 20)
    # assert rect.top_right == Vec2(20, 20)
    # assert rect.bottom_left == Vec2(10, 10)
    # assert rect.bottom_right == Vec2(20, 10)
    # assert rect.contains(Vec2(15, 15))
    # assert rect.contains(Vec2(10, 10))
    # assert rect.contains(Vec2(20, 20))
    # assert not rect.contains(Vec2(5, 5))
    # assert not rect.contains(Vec2(25, 25))
    # assert not rect.contains(Vec2(15, 25))
    # assert not rect.contains(Vec2(25, 15))
    # assert not rect.contains(Vec2(5, 15))
    # assert not rect.contains(Vec2(15, 5))
    # assert not rect.contains(Vec2(5, 25))

    # assert rect.intersects(Rect2(Vec2(15, 15), Vec2(25, 25)))
    # assert rect.intersects(Rect2(Vec2(15, 15), width=10, height=10))
    # assert rect.intersects(Rect2(Vec2(15, 15), size=Vec2(10, 10)))   

    # assert rect + Vec2(10, 10) == Rect2(Vec2(20, 20), Vec2(30, 30))
    # assert rect.expanded(20) == Rect2(Vec2(0, 0), Vec2(30, 30))    


    # assert VecN(1, 2, 3) == VecN(1, 2, 3)
    # assert VecN(1, 2, 3) != VecN(1, 2, 4)
    # assert VecN(1, 2, 3) != VecN(1, 2, 3, 4)
    # assert VecN(1, 2, 3) != VecN(1, 2)
    # assert VecN(1, 2, 3) == VecN([1, 2, 3])
    # assert VecN(1, 2, 3) == VecN((1, 2, 3))
    # assert VecN(1, 2, 3) == VecN(np.array([1, 2, 3]))

    # assert Vec2(1, 2) == Vec2(1, 2)
    # assert Vec2(1, 2) != Vec2(1, 3)
    # assert Vec2(1, 2) == VecN(1, 2)
    
    # assert Vec2(1, 2) == VecN([1, 2])

    # assert Vec3((1,2,3)) == VecN(1, 2, 3)
    # assert Vec3(1,2,3) != Vec2(1, 2)
    # assert Vec3(1,2,3).xy == Vec2(1, 2)

    # assert Vec3(1,2,3) != None
    # assert None != Vec3(1,2,3)

    # v3111 = Vec3(1,1,1)
    # v3111.xy += Vec2(1,1)
    # assert v3111 == Vec3(2,2,1)

    # assert Vec2(1, 2) + Vec2(1, 2) == Vec2(2, 4)
    # assert Vec2(1, 2) + 2 == Vec2(3, 4)
    # assert Vec2(1, 2) * 2 == Vec2(2, 4)
    # assert Vec2(1, 2) * Vec2(2, 2) == Vec2(2, 4)
    # assert Vec2(1, 2) * Vec2(2, 3) == Vec2(2, 6)
    # assert Vec2(1, 2) / 2 == Vec2(0.5, 1)
    # assert Vec2(1, 2) / Vec2(2, 2) == Vec2(0.5, 1)
    # assert Vec2(1, 2) / Vec2(2, 3) == Vec2(0.5, 2/3)
    # assert Vec2(1, 2) // Vec2(2, 3) == Vec2(0, 0)