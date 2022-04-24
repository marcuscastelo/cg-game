from dataclasses import dataclass, field
import math
from mimetypes import init
import time
from typing import Callable
import numpy as np

from OpenGL import GL as gl
from utils.geometry import Vec2, Vec3
from utils.logger import LOGGER
from app_state import MVPManager

from shader import Shader

from transformation_matrix import Transform

class Element:
    def __init__(self, initial_transform: Transform = None):
        self._last_physics_update = 0 # Used for physics updates
        self.__destroyed = False
        self.speed = 0.5

        self._render_primitive = gl.GL_TRIANGLES

        self._vertices = []
        self._init_vertices()

        self.transform = initial_transform if initial_transform is not None else Transform()
        assert isinstance(self.transform, Transform), f"Transform must be of type Transform, not {type(self.transform)}"

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

        # self.mvp_manager = MVPManager()
        # self.mvp_manager.translation = self.transform._translation # TODO: mvp_manager should use Transform class

    def _init_vertices(self):
        raise NotImplementedError("Abstract method, please implement in subclass")

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(id={str(id(self))[-5:]}, x={self.x}, y={self.y}, z={self.z})'



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
        dx = np.cos(self.angle + math.radians(90)) * intensity * self.speed
        dy = np.sin(self.angle + math.radians(90)) * intensity * self.speed
        self.transform.translation.xy += Vec2(dx, dy)

    def rotate(self, angle: float):
        # Rotate over Z axis (2D)
        self.transform.rotation.z += angle

    @property
    def x(self):
        return self.transform.translation.x
    
    @x.setter
    def x(self, value: float):
        self.transform.translation.x = value

    @property
    def y(self):
        return self.transform.translation.y

    @y.setter
    def y(self, value: float):
        self.transform.translation.y = value

    @property # No setter, because it's a read-only property (2D only)
    def z(self):
        return self.transform.translation.z


    @property
    def angle(self):
        return self.transform.rotation.z

    @angle.setter
    def angle(self, value: float):
        self.transform.rotation.z = value

    def _physics_update(self):
        raise NotImplementedError("Abstract method, please implement in subclass")

    def update(self):
        if self.destroyed:
            LOGGER.log_warning(f'Trying to update destroyed element {self}')
            return

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
        self.shader.set_uniform_matrix('transformation', self.transform.model_matrix)

        # Draw the triangles
        # gl.glColor3f(1.0, 0.0, 0.0)
        gl.glDrawArrays(self._render_primitive, 0, len(self._vertices))

    @property
    def destroyed(self):
        return self.__destroyed

    def destroy(self):
        if self.destroyed:
            # raise RuntimeError(f'Trying to destroy already destroyed element {self}')
            LOGGER.log_warning(f'Trying to destroy already destroyed element {self}')
            return
    
        LOGGER.log_debug(f"{self} marked for destruction")
        self.__destroyed = True