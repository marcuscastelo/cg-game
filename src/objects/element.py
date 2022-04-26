import math
import time
from typing import TYPE_CHECKING
import numpy as np

from OpenGL import GL as gl
from utils.geometry import Rect2, Vec2
from utils.logger import LOGGER

from shader import Shader

from transformation_matrix import Transform

if TYPE_CHECKING:
    from world import World

class Element:
    '''
    An abstract class for all the elements in the game
    '''
    
    def __init__(self, world: 'World', initial_transform: Transform = None):
        '''
        Initialize the element inside the world, with an optional initial transform
        '''

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

    def _init_vertices(self):
        '''
        Pure virtual method, must be implemented in subclass. Should initialize the vertices of the element
        Example:
            self._vertices = [
                -0.5, -0.5, 0.0,
                0.5, -0.5, 0.0,
                0.5, 0.5, 0.0,
                -0.5, 0.5, 0.0
            ]
        '''
        raise NotImplementedError("Abstract method, please implement in subclass")

    def __repr__(self) -> str:
        '''
        Return a string representation of the element
        '''
        return f'{self.__class__.__name__}(id={str(id(self))[-5:]}, x={self.x}, y={self.y}, z={self.z})'


    # Create a bounding box
    @staticmethod
    def get_bounding_box(elem: 'Element') -> Rect2:
        min_x = min(elem._vertices[::3])
        min_y = min(elem._vertices[1::3])
        max_x = max(elem._vertices[::3])
        max_y = max(elem._vertices[1::3])

        vertices = np.array([
            [min_x, min_y, 0, 0],
            [max_x, max_y, 0, 0]
        ])

        # Transform the vertices
        vertices = vertices @ elem.transform.model_matrix.T

        start = Vec2(vertices[0, 0], vertices[0, 1])
        end = Vec2(vertices[1, 0], vertices[1, 1])

        return Rect2(start, end) + elem.transform.translation.xy # FIXME: why do we need to add the translation here?

    
    def _on_outside_screen(self, screen_rect: Rect2):
        self.destroy()

    def move(self, intensity: float = 1.0):
        '''
        Move the element forward according to the current rotation
        '''
        dx = np.cos(self.angle + math.radians(90)) * intensity * self.speed
        dy = np.sin(self.angle + math.radians(90)) * intensity * self.speed
        self.transform.translation.xy += Vec2(dx, dy)

        self_rect = Element.get_bounding_box(self)
        screen_rect = Rect2(-1, -1, 1, 1).expanded(1) #TODO: change this to the screen size constant

        if not screen_rect.intersects(self_rect):
            self._on_outside_screen(screen_rect)


    def rotate(self, angle: float):
        '''
        Rotates the element on the Z axis (2D rotation)
        angle: angle in radians
        '''
        # Rotate over Z axis (2D)
        self.transform.rotation.z += angle

    @property
    def x(self):
        '''
        Get the x coordinate of the element
        '''
        return self.transform.translation.x
    
    @x.setter
    def x(self, value: float):
        '''
        Set the x coordinate of the element
        '''
        self.transform.translation.x = value

    @property
    def y(self):
        '''
        Get the y coordinate of the element
        '''
        return self.transform.translation.y

    @y.setter
    def y(self, value: float):
        '''
        Set the y coordinate of the element
        '''
        self.transform.translation.y = value

    @property # No setter, because it's a read-only property (2D only)
    def z(self):
        '''
        Get the z coordinate of the element (no setter available, since we're in 2D)
        '''
        return self.transform.translation.z

    @property
    def angle(self):
        '''
        Get the angle of the element on the Z axis
        '''
        return self.transform.rotation.z

    @angle.setter
    def angle(self, value: float):
        '''
        Set the angle of the element on the Z axis
        '''
        self.transform.rotation.z = value

    def _physics_update(self, delta_time: float):
        '''
        Pure virtual method, must be implemented in subclass. Should update the element's physics
        It is called every physics update (approx. 50 times per second)
        '''
        raise NotImplementedError("Abstract method, please implement in subclass")

    def update(self):
        '''
        Update the element, called every frame.
        If overridden, make sure to call the super method.
        Not intended to be overridden.
        '''
        if self.destroyed:
            LOGGER.log_warning(f'Trying to update destroyed element {self}')
            return

        if (delta_time := time.time() - self._last_physics_update) > 1/50:
            self._physics_update(delta_time)
            self._last_physics_update = time.time()

        self._render()
        
    def _render(self):
        '''
        Basic rendering method. Can be overridden in subclass.
        '''
        # Bind the shader and VAO (VBO is bound in the VAO)
        gl.glBindVertexArray(self.vao)
        # gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.vbo)
        self.shader.use()

        # Set the transformation matrix
        self.shader.set_uniform_matrix('transformation', self.transform.model_matrix)

        # Draw the vertices according to the primitive
        gl.glDrawArrays(self._render_primitive, 0, len(self._vertices))

    @property
    def destroyed(self):
        '''
        Returns whether the element is destroyed or not
        '''
        return self.__destroyed

    def destroy(self):
        '''
        Destroys the element
        '''
        if self.destroyed:
            # raise RuntimeError(f'Trying to destroy already destroyed element {self}')
            LOGGER.log_warning(f'Trying to destroy already destroyed element {self}')
            return
    
        LOGGER.log_debug(f"{self} marked for destruction")
        self.__destroyed = True