'''
Membros:       
'''

from threading import Thread

import glfw
import OpenGL.GL as gl

from threading import Thread

from utils.logger import LOGGER

from constants import WINDOW_SIZE
from app_state import APP_VARS, OpenGLScene
from gui import AppGui
from input.input_system import INPUT_SYSTEM as IS, set_glfw_callbacks

def create_window():
    '''
    Creates a GLFW window and returns it.
    this function also sets things like the window size, the window title, opengl context, etc.
    '''
    LOGGER.log_trace("Initializing GLFW", 'create_window')
    glfw.init() # Initialize GLFW (just in case we call from another thread or something)

    LOGGER.log_trace("Setting window hints", 'create_window')
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, gl.GL_TRUE)
    glfw.window_hint(glfw.RESIZABLE, gl.GL_FALSE)


    LOGGER.log_trace("Creating window", 'create_window')
    window = glfw.create_window(*WINDOW_SIZE, "CG Trab 1", monitor=None, share=None)

    LOGGER.log_trace("Enabling VSync", 'create_window')
    glfw.swap_interval(1)

    glfw.make_context_current(window)
    glfw.show_window(window)

    LOGGER.log_info("Window created", 'create_window')
    return window

def glfw_thread():
    '''
    This function runs in a separate thread. 
    It is the whole OpenGL application.
    We are using a separate thread so that we can render the GUI in the main thread.
    '''
    LOGGER.log_trace("Creating window", 'glfw_thread')
    window = create_window()

    set_glfw_callbacks(window)

    # Enable depth test
    LOGGER.log_trace("Enabling depth test", 'glfw_thread')
    gl.glEnable(gl.GL_DEPTH_TEST)
    gl.glDepthFunc(gl.GL_LESS)
    
    # Enable blending
    LOGGER.log_trace("Enabling blending", 'glfw_thread')
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

    # Create the scene (world)
    LOGGER.log_info("Preparing world", 'glfw_thread')
    world = APP_VARS.world
    world.setup_scene()

    while not glfw.window_should_close(window) and not APP_VARS.closing:
        glfw.poll_events()

        def render():
            # gl.glUniformMatrix4fv(mvp_loc, 1, gl.GL_FALSE, STATE.mvp_manager.mvp)

            gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
            gl.glClearColor(1.0, 1.0, 1.0, 1.0)

            # Update the scene
            world.update()

        render()

        glfw.swap_buffers(glfw.get_current_context())
    
    LOGGER.log_info("GLFW thread is closing", 'glfw_thread')
    APP_VARS.closing = True


def _set_signal_handler():
    '''
    Insted of just closing the main thread and hanging the program, 
    we can use this function to close the program properly.
    It updates a variable, which will cause all threads to close on the next iteration.
    '''
    # Handle CTRL+C (SIGINT) signal
    def signal_handler(*_):
        APP_VARS.closing = True

    import signal
    signal.signal(signal.SIGINT, signal_handler)


def main():
    _set_signal_handler() # Handle CTRL+C (SIGINT) signal to close the app (2 threads)
    
    LOGGER.log_info("Starting app", 'main')

    LOGGER.log_trace("Init Glfw", 'main')
    glfw.init()
    
    LOGGER.log_trace("Init GUI", 'main')
    gui = AppGui() # GUI thread (main thread)

    LOGGER.log_trace("Start GLFW thread", 'main')
    t = Thread(target=glfw_thread)
    t.start() # GLFW thread (2nd thread)

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
