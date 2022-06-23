'''
Entrega 1 - Computação Gráfica (SCC 0250)
Membros:       
    Dalton Hiroshi Sato
    Marcus Vinicius Castelo Branco Martins
    Pedro Guerra Lourenço
    Vinícius Eduardo de Araújo
    Vitor Souza Amim
'''

from threading import Thread
import time

import glfw
import OpenGL.GL as gl

from threading import Thread

from utils.logger import LOGGER
from app_vars import APP_VARS

from constants import GUI_WIDTH, WINDOW_SIZE
from input.input_system import setup_input_system, INPUT_SYSTEM as IS

from gui import AppGui

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
    glfw.window_hint(glfw.RESIZABLE, gl.GL_FALSE)


    LOGGER.log_trace("Creating window", 'create_window')
    window = glfw.create_window(*WINDOW_SIZE, "CG Trab 1", monitor=None, share=None)
    glfw.set_window_pos(window, GUI_WIDTH, 0)
    glfw.make_context_current(window)
    glfw.show_window(window)

    LOGGER.log_trace("Disabling mouse", 'create_window')
    glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_DISABLED);

    LOGGER.log_trace("Enabling VSync", 'create_window')
    glfw.swap_interval(1)

    LOGGER.log_info("Window created", 'create_window')


    gl.glEnable(gl.GL_CULL_FACE);  
    gl.glCullFace(gl.GL_FRONT);  
    gl.glFrontFace(gl.GL_CW);  

    return window

def glfw_thread():
    '''
    This function runs in a separate thread. 
    It is the whole OpenGL application.
    We are using a separate thread so that we can render the GUI in the main thread.
    '''
    LOGGER.log_trace("Creating window", 'glfw_thread')
    window = create_window()

    gl.glEnable(gl.GL_BLEND) # Enable blending
    gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA) # Set blending function

    gl.glEnable(gl.GL_DEPTH_TEST)

    camera = APP_VARS.camera

    def key_callback(window, key: int, scancode, action: int, mods: int):
        if APP_VARS.cursor.capturing and key == glfw.KEY_ESCAPE and action == glfw.RELEASE:
            APP_VARS.cursor.capturing = False
            glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_NORMAL);

        camera.on_key(window, key, scancode, action, mods)

    def cursor_pos_callback(window, xpos, ypos):
        if APP_VARS.cursor.capturing:
            camera.on_cursor_pos(window, xpos, ypos)

    def mouse_button_callback(window, button: int, action: int, mods: int):
        if not APP_VARS.cursor.capturing and action == glfw.PRESS:
            APP_VARS.cursor.capturing = True
            APP_VARS.cursor.capturing = True
            glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_DISABLED);

    setup_input_system(window)
    IS.add_key_callback(key_callback)
    IS.add_mouse_button_callback(mouse_button_callback)
    IS.add_cursor_pos_callback(cursor_pos_callback)

    # Create the scene (world)
    LOGGER.log_info("Preparing world", 'glfw_thread')
    world = APP_VARS.world
    world.setup_scene()

    # Background color
    R: float = 32/255 
    G: float = 31/255 
    B: float = 65/255 

    while not glfw.window_should_close(window) and not APP_VARS.closing:
        glfw.poll_events() # Process input events (keyboard, mouse, etc)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        gl.glClearColor(R, G, B, 1.0)

        def render():
            world.update()

        render()

        APP_VARS.game_fps.update_calc_fps(time.time())
        print(f'Game FPS: {APP_VARS.game_fps.fps}')
        glfw.swap_buffers(glfw.get_current_context()) # Swap the buffers (drawing buffer -> screen)

    LOGGER.log_info("GLFW thread is closing", 'glfw_thread')
    APP_VARS.closing = True # Make the GUI close too

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
    

    LOGGER.log_trace("Start GLFW thread", 'main')
    t = Thread(target=glfw_thread)
    t.start() # GLFW thread (2nd thread)

    _tries = 0
    while len(APP_VARS.world.elements) < 2: # TODO: remove gambiarra feia
        LOGGER.log_debug("Hack: waiting for cube to be spawned...", 'main')
        time.sleep(0.1)
        if _tries > 10:
            exit(1)
        _tries += 1

    LOGGER.log_trace("Init GUI", 'main')
    gui = AppGui() # GUI thread (main thread)

    LOGGER.log_trace("Start GUI", 'main')
    gui.run()

    LOGGER.log_info("GUI Has been closed, waiting for GLFW to close...", 'main')
    t.join()
    LOGGER.log_info("GLFW thread has been closed", 'main')

    LOGGER.log_trace("Terminating Glfw", 'main')
    glfw.terminate()
    LOGGER.log_info("App has been closed gracefully", 'main')

if __name__ == "__main__":
    main()
