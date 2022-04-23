from dataclasses import dataclass
import math
from mimetypes import init
from typing import Callable
import numpy as np

from OpenGL import GL as gl
from app_state import MVPManager

from shader import Shader
import keyboard

BASE_SIZE = 1/16 * (1 - (-1))

@dataclass
class ShipController:
    """
    This class is used to store the movement of the ship.
    User input is stored in this class. (in the current frame)
    """
    input_movement: float = 0
    input_rotation: float = 0
    enabled = False
    keybinds = {
        "forward": "w",
        "backward": "s",
        "left": "a",
        "right": "d",
    }

    def enable(self):
        self.enabled = True
    def disable(self):
        self.enabled = False

    def process_input(self):
        if not self.enabled:
            return
            
        TRANSLATION_STEP = 0.04
        ROTATION_STEP = 2*math.pi/360 * 5
        forward = self.keybinds["forward"]
        backward = self.keybinds["backward"]
        left = self.keybinds["left"]
        right = self.keybinds["right"]

        if keyboard.is_pressed('shift'):
            TRANSLATION_STEP *= 2
            ROTATION_STEP *= 2
        elif keyboard.is_pressed('ctrl'):
            TRANSLATION_STEP *= 0.5
            ROTATION_STEP *= 0.5

        if keyboard.is_pressed(forward):
            self.input_movement = TRANSLATION_STEP
        elif keyboard.is_pressed(backward):
            self.input_movement = -TRANSLATION_STEP
        else:
            self.input_movement = 0

        if keyboard.is_pressed(left):
            self.input_rotation = ROTATION_STEP
        elif keyboard.is_pressed(right):
            self.input_rotation = -ROTATION_STEP
        else:
            self.input_rotation = 0


@dataclass(init=False)
class Ship:
    x: float = 0
    y: float = 0
    z: float = 0
    speed: float = 1
    angle: float = 0
    energy: float = 1 # [1, 2]: indicates glow intensity

    def __init__(self, initial_coords: tuple[float, float, float] = (0,0,0)):
        self._vertices = [ # 2D Triangle
            # X, Y, Z
            -BASE_SIZE, -BASE_SIZE*2*0.87*1/3, 0.0,
            +BASE_SIZE, -BASE_SIZE*2*0.87*1/3, 0.0,
            0.0,        +BASE_SIZE*2*0.87*2/3, 0.0,
        ]

        self.controller = ShipController()

        self.x, self.y, self.z = initial_coords

        self.vao = gl.glGenVertexArrays(1)
        self.vbo = gl.glGenBuffers(1)

        gl.glBindVertexArray(self.vao)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.vbo)

        # Set the vertex buffer data
        gl.glBufferData(gl.GL_ARRAY_BUFFER, len(self._vertices)*4, (gl.GLfloat * len(self._vertices))(*self._vertices), gl.GL_DYNAMIC_DRAW)

        self.shader = Shader('shaders/ship/ship.vert', 'shaders/ship/ship.frag')
        self.shader.use()

        gl.glEnableVertexAttribArray(0)
        gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, gl.GL_FALSE, 0, None)

        gl.glEnableVertexAttribArray(1)
        gl.glVertexAttribPointer(1, 1, gl.GL_FLOAT, gl.GL_FALSE, 0, None)

        gl.glUseProgram(0) # Unbind the shader
        gl.glBindVertexArray(0) # Unbind the VAO
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0) # Unbind the VBO

        self.mvp_manager = MVPManager()
        self.mvp_manager.translation = (self.x, self.y)

    def move(self, intensity: float):
        self.x += np.cos(self.angle + math.radians(90)) * intensity * self.speed
        self.y += np.sin(self.angle + math.radians(90)) * intensity * self.speed
        self.mvp_manager.translation = (self.x, self.y)

    def rotate(self, angle: float):
        self.angle += angle
        self.mvp_manager.rotation_angle = self.angle # TODO: support 3D rotation


    def _physic_update(self):
        if self.controller.input_movement != 0:
            self.move(self.controller.input_movement)
        if self.controller.input_rotation != 0:
            self.rotate(self.controller.input_rotation)

    def render(self):
        self.controller.process_input()
        
        # TODO: process physics 1/50th of a second
        self._physic_update()

        # Bind the shader and VAO (VBO is bound in the VAO)
        gl.glBindVertexArray(self.vao)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.vbo)
        self.shader.use()

        # Set the transformation matrix
        self.shader.set_uniform_matrix('transformation', self.mvp_manager.mvp)

        # Draw the triangles
        gl.glColor3f(1.0, 0.0, 0.0)
        gl.glDrawArrays(gl.GL_TRIANGLES, 0, len(self._vertices))
        
        pass

    def register_keyboard_controls(self):
        # TRANSLATION_STEP = 0.04
        # ROTATION_STEP = 2*math.pi/360 * 5
        # SCALE_STEP = 0.2

        # def callback_gen(step: float, callback: Callable[[float], None]):
        #     # if shift is pressed, the step is increased
        #     def callback_wrapper(*_args):
        #         print(f"shift is pressed: {keyboard.is_pressed('shift')}")
        #         if keyboard.is_pressed('shift'):
        #             callback(step * 2)
        #         elif keyboard.is_pressed('ctrl'):
        #             callback(step / 2)
        #         else:
        #             callback(step)
            
        #     return callback_wrapper


        # keyboard.on_press_key('w', callback_gen(TRANSLATION_STEP, lambda step: self.move(step)))
        # keyboard.on_press_key('s', callback_gen(TRANSLATION_STEP, lambda step: self.move(-step)))
        # # keyboard.on_press_key('a', callback_gen(TRANSLATION_STEP, lambda step: self.mvp_manager.translate(-step, 0.0)))
        # # keyboard.on_press_key('d', callback_gen(TRANSLATION_STEP, lambda step: self.mvp_manager.translate(step, 0.0)))
        # keyboard.on_press_key('q', callback_gen(ROTATION_STEP, lambda step: self.rotate(step)))
        # keyboard.on_press_key('e', callback_gen(ROTATION_STEP, lambda step: self.rotate(-step)))
        # keyboard.on_press_key('z', callback_gen(SCALE_STEP, lambda step: self.mvp_manager.zoom(step)))
        # keyboard.on_press_key('x', callback_gen(SCALE_STEP, lambda step: self.mvp_manager.zoom(-step)))
        pass
