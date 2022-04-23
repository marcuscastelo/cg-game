from cgi import test
from dataclasses import dataclass
import math
from threading import Thread
from typing import Callable

import glfw
import OpenGL.GL as gl

from threading import Thread

from utils.logger import LOGGER
from utils.geometry import Vec2Int

from constants import WINDOW_SIZE
from app_state import STATE
from gui import AppGui

import numpy as np

import keyboard
from objects.ship import Ship

from shader import Shader

def create_window():
    glfw.init()
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    window = glfw.create_window(*WINDOW_SIZE, "Simple Window", monitor=None, share=None)
    glfw.make_context_current(window)
    glfw.show_window(window)
    return window

def glfw_thread():
    window = create_window()

    ship1 = Ship((-0.5, -0.5, 0))
    ship2 = Ship((0.5, 0.5, 0))

    # mvp_loc = gl.glGetUniformLocation(test_shader.program, "mvp")

    # # Use a FBO instead of the default framebuffer
    # fbo = gl.glGenFramebuffers(1)
    # gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, fbo)

    # # Create a texture to render to
    # texture = gl.glGenTextures(1)
    # gl.glBindTexture(gl.GL_TEXTURE_2D, texture)
    # gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGB, *WINDOW_SIZE, 0, gl.GL_RGB, gl.GL_UNSIGNED_BYTE, None)
    # gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
    # gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)
    # gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP_TO_EDGE)
    # gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP_TO_EDGE)

    # # Attach the texture to the FBO
    # gl.glFramebufferTexture2D(gl.GL_FRAMEBUFFER, gl.GL_COLOR_ATTACHMENT0, gl.GL_TEXTURE_2D, texture, 0)

    # STATE.texture = texture

    while not glfw.window_should_close(window) and not STATE.closing:
        glfw.poll_events()

        def render():
            # gl.glUniformMatrix4fv(mvp_loc, 1, gl.GL_FALSE, STATE.mvp_manager.mvp)

            gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
            gl.glClearColor(1.0, 1.0, 1.0, 1.0)

            ship1.render()
            ship2.render()

        # gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, fbo)
        # render()

        # gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, 0)
        render()

        glfw.swap_buffers(glfw.get_current_context())
    
    LOGGER.log_info("GLFW thread is closing", 'glfw_thread')
    STATE.closing = True

def register_keyboard_controls():
    TRANSLATION_STEP = 0.04
    ROTATION_STEP = 2*math.pi/360 * 5
    SCALE_STEP = 0.2

    def callback_gen(step: float, callback: Callable[[float], None]):
        # if shift is pressed, the step is increased
        def callback_wrapper(*_args):
            print(f"shift is pressed: {keyboard.is_pressed('shift')}")
            if keyboard.is_pressed('shift'):
                callback(step * 2)
            elif keyboard.is_pressed('ctrl'):
                callback(step / 2)
            else:
                callback(step)
        
        return callback_wrapper


    keyboard.on_press_key('w', callback_gen(TRANSLATION_STEP, lambda step: STATE.mvp_manager.translate(0.0, step)))
    keyboard.on_press_key('s', callback_gen(TRANSLATION_STEP, lambda step: STATE.mvp_manager.translate(0.0, -step)))
    keyboard.on_press_key('a', callback_gen(TRANSLATION_STEP, lambda step: STATE.mvp_manager.translate(-step, 0.0)))
    keyboard.on_press_key('d', callback_gen(TRANSLATION_STEP, lambda step: STATE.mvp_manager.translate(step, 0.0)))
    keyboard.on_press_key('q', callback_gen(ROTATION_STEP, lambda step: STATE.mvp_manager.rotate(step)))
    keyboard.on_press_key('e', callback_gen(ROTATION_STEP, lambda step: STATE.mvp_manager.rotate(-step)))
    keyboard.on_press_key('z', callback_gen(SCALE_STEP, lambda step: STATE.mvp_manager.zoom(step)))
    keyboard.on_press_key('x', callback_gen(SCALE_STEP, lambda step: STATE.mvp_manager.zoom(-step)))



def main():
    register_keyboard_controls()

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