from dataclasses import dataclass
import math
from mimetypes import init
import time
from typing import Callable
import numpy as np

from OpenGL import GL as gl
from app_state import MVPManager

from shader import Shader
import keyboard

@dataclass
class Element:
    z: float = 0 # TODO: clean up the code (remove z or add to mvp_manager)
    speed = 0.5
    _vertices = []
    _render_primitive = gl.GL_TRIANGLES
    _destroyed = False

    def __init__(self, initial_coords: tuple[float, float, float] = (0,0,0)):
        self._init_vertices()
        self._last_physics_update = 0

        x, y, self.z = initial_coords

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
        self.mvp_manager.translation = (x, y)

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(id={str(id(self))[-5:]}, x={self.x}, y={self.y}, z={self.z})'


    def _init_vertices(self):
        raise NotImplementedError("Abstract method, please implement in subclass")

    # Create a bounding box
    @staticmethod
    def get_bounding_box(elem: 'Element'):
        xs = elem._vertices[::3]
        ys = elem._vertices[1::3]
        zs = elem._vertices[2::3]
        hs = [0] * len(xs)

        vertices = np.array(list(zip(xs, ys, zs, hs)), dtype=np.float32)
        # Each row is a vertex (x, y, z, h)
        # h is the harmonic variable (used for nothing)
        # We need to scale, translate and rotate the vertices
        # to get the bounding box

        transformed_vertices = vertices
        # transformed_vertices = np.matmul(elem.mvp_manager.mvp, vertices.T)

        min_x = min(transformed_vertices, key=lambda v: v[0])[0]
        min_y = min(transformed_vertices, key=lambda v: v[1])[1]
        max_x = max(transformed_vertices, key=lambda v: v[0])[0]
        max_y = max(transformed_vertices, key=lambda v: v[1])[1]

        min_x += elem.x
        min_y += elem.y
        max_x += elem.x
        max_y += elem.y

        return (min_x, min_y, max_x, max_y)

    def collides_with(self, other: 'Element') -> bool:
        # Based on vertices (compare with other.vertices)
    
        # Get the bounding boxes
        self_bounding_box = Element.get_bounding_box(self)
        other_bounding_box = Element.get_bounding_box(other)

        # Check if the bounding boxes intersect
        if self_bounding_box[0] > other_bounding_box[2] or self_bounding_box[2] < other_bounding_box[0]:
            return False
        if self_bounding_box[1] > other_bounding_box[3] or self_bounding_box[3] < other_bounding_box[1]:
            return False
        
        # Check if the vertices intersect
        self_xs = self._vertices[::3]
        self_ys = self._vertices[1::3]

        other_xs = other._vertices[::3]
        other_ys = other._vertices[1::3]

        self_vertices = zip(self_xs, self_ys)
        other_vertices = zip(other_xs, other_ys)

        # for self_vertex in self_vertices:
        #     for other_vertex in other_vertices:
        #         if self_vertex[0] == other_vertex[0] and self_vertex[1] == other_vertex[1]:
        #             return True
        return True

    def move(self, intensity: float):
        self.x += np.cos(self.angle + math.radians(90)) * intensity * self.speed
        self.y += np.sin(self.angle + math.radians(90)) * intensity * self.speed
        self.mvp_manager.translation = (self.x, self.y)

    def rotate(self, angle: float):
        self.mvp_manager.rotate(angle) # TODO: support 3D rotation

    @property
    def x(self):
        return self.mvp_manager.translation_x
    
    @x.setter
    def x(self, value: float):
        self.mvp_manager.translation_x = value

    @property
    def y(self):
        return self.mvp_manager.translation_y

    @y.setter
    def y(self, value: float):
        self.mvp_manager.translation_y = value

    @property
    def angle(self):
        return self.mvp_manager.rotation_angle

    @angle.setter
    def angle(self, value: float):
        self.mvp_manager.rotation_angle = value

    def _physics_update(self):
        raise NotImplementedError("Abstract method, please implement in subclass")

    def update(self):
        if time.time() - self._last_physics_update > 1/50:
            self._physics_update()
            self._last_physics_update = time.time()

        self._render()
        
    def _render(self):
        # Bind the shader and VAO (VBO is bound in the VAO)
        gl.glBindVertexArray(self.vao)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.vbo)
        self.shader.use()

        # Set the transformation matrix
        self.shader.set_uniform_matrix('transformation', self.mvp_manager.mvp)

        # Draw the triangles
        gl.glColor3f(1.0, 0.0, 0.0)
        gl.glDrawArrays(self._render_primitive, 0, len(self._vertices))

    
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

    def destroy(self):
        self._destroyed = True