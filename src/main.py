'''
Entrega 1 - Computação Gráfica (SCC 0250)
Membros:       
    Dalton Hiroshi Sato
    Marcus Vinicius Castelo Branco Martins
    Pedro Guerra Lourenço
    Vinícius Eduardo de Araújo
    Vitor Souza Amim
'''

from colorsys import hsv_to_rgb
from dataclasses import dataclass
import math
from shutil import move
from threading import Thread
import time

import glfw
import OpenGL.GL as gl

from threading import Thread
import glm

from utils.logger import LOGGER
from app_vars import APP_VARS
from camera import Camera

from constants import GUI_WIDTH, WINDOW_SIZE
from gl_abstractions.layout import Layout
from gl_abstractions.shader import ShaderDB
from gl_abstractions.texture import Texture2D
from gl_abstractions.vertex_array import VertexArray
from gl_abstractions.vertex_buffer import VertexBuffer
from input.input_system import setup_input_system, INPUT_SYSTEM as IS
from objects._2d.screens.lose_screen import LoseScreen
from objects._2d.screens.win_screen import WinScreen
from objects.cube import Cube
from objects._2d._2dworld import World

from gui import AppGui
import constants

import numpy as np

from objects.element import Element

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


    return window

def model():
    mat_model = glm.mat4(1.0) # matriz identidade (não aplica transformação!)
    mat_model = np.array(mat_model)    
    return mat_model

def view(camera: Camera):
    mat_view = glm.lookAt(camera.cameraPos, camera.cameraPos + camera.cameraFront, camera.cameraUp);
    mat_view = np.array(mat_view)
    return mat_view

def projection():
    # perspective parameters: fovy, aspect, near, far
    mat_projection = glm.perspective(glm.radians(45.0), constants.WINDOW_SIZE[0]/constants.WINDOW_SIZE[1], 0.1, 100.0)
    mat_projection = np.array(mat_projection)    
    return mat_projection
    

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

    camera = Camera()

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

    # TODO: refactor
    setup_input_system(window)
    IS.add_key_callback(key_callback)
    IS.add_mouse_button_callback(mouse_button_callback)
    IS.add_cursor_pos_callback(cursor_pos_callback)

    # glfw.set_key_callback(window, key_callback)
    # glfw.set_cursor_pos_callback(window, cursor_pos_callback)
    # glfw.set_mouse_button_callback(window, mouse_button_callback)
    #### 


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


    # cubes_layout = Layout([('position', 3)])
    # cubes_vbo = VertexBuffer(layout=cubes_layout, data=cube_vertices)
    # cubes_vao = VertexArray()
    # cubes_vao.upload_vertex_buffer(cubes_vbo)
    # cube_program = ShaderDB.get_instance().get_shader('simple_red')
    # Render loop: keeps running until the window is closed or the GUI signals to close

    _last_frame_time = time.time()


    while not glfw.window_should_close(window) and not APP_VARS.closing:
        glfw.poll_events() # Process input events (keyboard, mouse, etc)

        # Actual rendering of the scene
        def render_1st_deliver():
            gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
            gl.glClearColor(R, G, B, 1.0)

            # Decides if player won, lose, or game is still going
            if world.is_player_victory():
                win_screen.update()
            elif world.is_player_defeat():
                lose_screen.update()
            else:
                world.update()
                pass

            # Special shortcut to reset scene
            if IS.just_pressed('r'):
                world.setup_scene()

            if IS.just_pressed('b'):
                APP_VARS.debug.show_bbox = not APP_VARS.debug.show_bbox

        def render_2nd_deliver():
            nonlocal _last_frame_time, camera
            gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
            gl.glClearColor(R, G, B, 1.0)   
            
            cube1: Cube = world.elements[0]
            cube2: Cube = world.elements[1]
            lose_screen: LoseScreen = world.elements[2]

            def draw(elem: Element):
                # cube.update()
                assert isinstance(elem, Element), 'Test code crashed, please rewrite this line'

                renderer = elem.shape_renderers[0]

                # TODO: multiply inside shader (GPU)
                # mat_model = model()
                mat_model = renderer.transform.model_matrix # TODO: use real model matrix
                mat_view = view(camera)
                mat_projection = projection()
                mat_transform = mat_projection @ mat_view @ mat_model

                if renderer.texture is not None:
                    renderer.texture.bind()

                renderer.shader.use()
                renderer.vao.bind()
                renderer.shader.upload_uniform_matrix4f('u_Transformation', mat_transform)
                
                gl.glDrawArrays(renderer.shape_spec.render_mode, 0, len(renderer.shape_spec.vertices))
            
            draw(cube1)
            draw(cube2)
            draw(lose_screen)


            t = time.time()
            camera.update(t - _last_frame_time)
            _last_frame_time = t

            if IS.just_pressed('r'):
                LOGGER.log_debug('Reseting camera...')
                camera.reset()

        # render_1st_deliver()
        render_2nd_deliver()

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
    while len(APP_VARS.world.elements) == 0:
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
