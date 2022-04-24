import math
import time
from turtle import width
from typing import TYPE_CHECKING, Callable
from math import cos, sin
from glm import clamp
import numpy as np

from OpenGL import GL as gl
from utils.geometry import Rect, Rect2, Vec2, Vec3
from utils.logger import LOGGER

from shader import Shader

from transformation_matrix import Transform

if TYPE_CHECKING:
    from world import World

class Element:
    def __init__(self, world: 'World', initial_transform: Transform = None):
        self.world = world
        world.add_element(self)

        self.transform = initial_transform if initial_transform is not None else Transform()
        assert isinstance(self.transform, Transform), f"Transform must be of type Transform, not {type(self.transform)}"
        
        self._last_physics_update = time.time() # Used for physics updates
        self.__destroyed = False
        self.speed = 0.5

        self._render_primitive = gl.GL_TRIANGLES

        self._vertices = []
        self._init_vertices()


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
    def get_bounding_box(elem: 'Element') -> Rect2:
        min_x = min(elem._vertices[::3])
        min_y = min(elem._vertices[1::3])
        max_x = max(elem._vertices[::3])
        max_y = max(elem._vertices[1::3])

        horiz_size = max_x - min_x
        vert_size = max_y - min_y

        start = Vec2(min_x, min_y)
        end = Vec2(max_x, max_y)

        return Rect2(start, end) * elem.transform.scale.xy + elem.transform.translation.xy

        
        

        # gl_vertices = np.array(elem._vertices) # [ x, y, z, x, y, z, ... ]
        # # LOGGER.log_debug(f'gl_vertices: {gl_vertices}')


        # tupled_vertices = np.array(gl_vertices).reshape((-1, 3)) # [ [x, y, z], [x, y, z], ... ]
        # # LOGGER.log_debug(f'tupled_vertices: {tupled_vertices}')
        
        # # Add the homogeneous coordinate (4th) dimension
        # tupled_vertices = np.insert(tupled_vertices, 3, 0, axis=1)
        # # LOGGER.log_debug(f'tupled_vertices: {tupled_vertices}')

        # transformed_vertices = tupled_vertices @ elem.transform.model_matrix.T # [ [x, y, z], [x, y, z], ... ]
        # # LOGGER.log_debug(f'transformed_vertices: {transformed_vertices}')

        # transformed_vertices = transformed_vertices.reshape((-1, 2)) # [ [x, y], [x, y], ... ]
        # LOGGER.log_debug(f'transformed_vertices: {transformed_vertices}')

        # min_x = transformed_vertices[:, 0].min()
        # min_y = transformed_vertices[:, 1].min()
        # max_x = transformed_vertices[:, 0].max()
        # max_y = transformed_vertices[:, 1].max()

        # LOGGER.log_debug(f'Bounding box: {(min_x, min_y, max_x, max_y)}')

        # return Rect.from_bbox((min_x, min_y, max_x, max_y))

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

    def move(self, intensity: float = 1.0):
        old_pos = self.transform.translation.xyz

        dx = np.cos(self.angle + math.radians(90)) * intensity * self.speed
        dy = np.sin(self.angle + math.radians(90)) * intensity * self.speed
        self.transform.translation.xy += Vec2(dx, dy)

        min_x, min_y, max_x, max_y = Element.get_bounding_box(self)
        if min_x < -1.05 or max_x > 1.05:
            LOGGER.log_debug(f"{self} moved out of horizontal bounds, reverting")
            # self.transform.translation.x = clamp(old_pos.x, -1.05, 1.05)
        if min_y < -1.05 or max_y > 1.05:
            LOGGER.log_debug(f"{self} moved out of vertical bounds, reverting")
            # self.transform.translation.y = clamp(old_pos.y, -1.05, 1.05)


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

    def _physics_update(self, delta_time: float):
        raise NotImplementedError("Abstract method, please implement in subclass")

    def update(self):
        if self.destroyed:
            LOGGER.log_warning(f'Trying to update destroyed element {self}')
            return

        if (delta_time := time.time() - self._last_physics_update) > 1/50:
            self._physics_update(delta_time)
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