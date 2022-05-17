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

import glfw
import OpenGL.GL as gl

from threading import Thread

from utils.logger import LOGGER
from app_vars import APP_VARS

from constants import WINDOW_SIZE
from input.input_system import set_glfw_callbacks, INPUT_SYSTEM as IS
from objects.screens.lose_screen import LoseScreen
from objects.screens.win_screen import WinScreen

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

    glfw.make_context_current(window)
    glfw.show_window(window)

    LOGGER.log_trace("Enabling VSync", 'create_window')
    glfw.swap_interval(1)

    LOGGER.log_info("Window created", 'create_window')
    return window

def glfw_run():
    '''
    This function runs in a separate thread. 
    It is the whole OpenGL application.
    We are using a separate thread so that we can render the GUI in the main thread.
    '''
    LOGGER.log_trace("Creating window", 'glfw_thread')
    window = create_window()

    gl.glEnable(gl.GL_BLEND) # Enable blending
    gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA) # Set blending function

    set_glfw_callbacks(window)

    # Create the scene (world)
    LOGGER.log_info("Preparing world", 'glfw_thread')
    world = APP_VARS.world
    world.setup_scene()

    # Background color
    R: float = 32/255 
    G: float = 31/255 
    B: float = 65/255 

    # Add win and lose screens to the world, so they can pop up when their condition os satisfied (end game)
    win_screen = WinScreen(world)
    lose_screen = LoseScreen(world)
    world.elements.remove(win_screen) # TODO: make this less hacky
    world.elements.remove(lose_screen) # TODO: make this less hacky



    # Render loop: keeps running until the window is closed or the GUI signals to close
    while not glfw.window_should_close(window) and not APP_VARS.closing:
        glfw.poll_events() # Process input events (keyboard, mouse, etc)

        # Actual rendering of the scene
        def render():
            gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
            gl.glClearColor(R, G, B, 1.0)

            # Decides if player won, lose, or game is still going
            if world.is_player_victory():
                win_screen.update()
            elif world.is_player_defeat():
                lose_screen.update()
            else:
                world.update()

            # Special shortcut to reset scene
            if IS.just_pressed('r'):
                world.setup_scene()

            if IS.just_pressed('b'):
                APP_VARS.debug.show_bbox = not APP_VARS.debug.show_bbox

        render() # Render to the default framebuffer (screen)

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
    
    LOGGER.log_info("Start glfw window and start game", 'main')
    glfw_run()

    LOGGER.log_trace("Terminating Glfw", 'main')
    glfw.terminate()
    LOGGER.log_info("App has been closed gracefully", 'main')

if __name__ == "__main__":
    main()
