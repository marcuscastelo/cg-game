import ctypes
from dataclasses import dataclass, field
import math
import os
import time
from typing import TYPE_CHECKING
import numpy as np

from OpenGL import GL as gl
from utils.geometry import Rect, Rect2, Vec2, Vec3
from utils.logger import LOGGER
from constants import FLOAT_SIZE, SCREEN_RECT

import imageio
from gl_abstractions.vertex_array import VertexArray
from gl_abstractions.vertex_buffer import VertexBuffer

from shader import Shader

from transformation_matrix import Transform

TEXTURED_SHADER = None
IMAGE: imageio.core.util.Array = imageio.imread('/home/marucs/Development_SSD/USP/2022/1_Sem/CG/cg-trab/textures/texure.jpg')[::-1,:,:] # TODO: relative path

from input.input_system import INPUT_SYSTEM as IS

if TYPE_CHECKING:
    from world import World

@dataclass
class Vertex:
    a_Position: Vec3
    a_TexCoord: Vec2

@dataclass
class VertexSpecification:
    vertices: list[Vertex]

    def to_np_array(self) -> np.ndarray:
        '''
        Returns a numpy array of the vertices
        '''
        vertices_continuos = np.array([[*v.a_Position, *v.a_TexCoord] for v in self.vertices], dtype=np.float32)
        vertices_flattened = vertices_continuos.flatten()
        return vertices_flattened

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

        self._vertex_specs = self._create_vertex_buffer()
        assert isinstance(self._vertex_specs, VertexSpecification), f"Vertex buffer must be of type VertexBuffer, not {type(self._vertex_specs)}"

        self._normal_vertex_specs = self._vertex_specs
        self._ouline_vertex_specs = self._vertex_specs
        # TODO: reenable 'T' keybind
        # if len(self._vertices) == 0:
        #     LOGGER.log_error(f'{self.__class__.__name__} id={id(self)} has no vertices')
        
        # if len(self._normal_vertices) == 0:
        #     LOGGER.log_warning(f'{self.__class__.__name__} id={id(self)} has no normal vertices, assuming all vertices are normal')
        #     self._normal_vertices = self._vertices

        # if len(self._ouline_vertices) == 0:
        #     LOGGER.log_warning(f'{self.__class__.__name__} id={id(self)} has no outline vertices, assuming all vertices are outline')
        #     self._ouline_vertices = self._vertices
        self._vertices = self._vertex_specs.to_np_array()

        # Vertex array object that will hold all other buffers
        self.vertex_array = VertexArray()
        self.vertex_buffer = VertexBuffer(self._vertices)
        
        # Bind the Vertex Array Object and then the Vertex Buffer Object 
        self.vertex_array.bind()
        self.vertex_buffer.bind()
        # Load shader and use it and save it for rendering
        global TEXTURED_SHADER
        if TEXTURED_SHADER is None:
            # FLAT_COLOR_SHADER = Shader('shaders/simple_red.vert', 'shaders/simple_red.frag')
            TEXTURED_SHADER = Shader('shaders/textured.vert', 'shaders/textured.frag')
            # pass
        self.shader = TEXTURED_SHADER

        # Enable vertex attribute position
        stride = 5 * FLOAT_SIZE # 3 for position, 2 for texcoord
        pos_offset = ctypes.cast(0 * FLOAT_SIZE, ctypes.c_void_p) # Position offset: 0 (first 3 floats)
        tex_offset = ctypes.cast(3 * FLOAT_SIZE, ctypes.c_void_p) # Texcoord offset: 3 (next 2 floats, after 3 floats for position)

        gl.glEnableVertexAttribArray(0)
        gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, gl.GL_FALSE, stride, pos_offset) # 3 position values per vertex

        gl.glEnableVertexAttribArray(1)
        gl.glVertexAttribPointer(1, 2, gl.GL_FLOAT, gl.GL_FALSE, stride, tex_offset) # 2 texture coordinates per vertex

        gl.glVertexAttribPointer(1, 2, gl.GL_FLOAT, gl.GL_FALSE, stride, tex_offset) # 2 texture coordinates per vertex


        print(f'Type of IMAGE: {type(IMAGE)}')

        self.texture = gl.glGenTextures(1) # TODO: generate once per different element (self._create_texture)
        LOGGER.log_debug(f'{self.__class__.__name__} id={id(self)} texture id={self.texture}')

        gl.glBindTexture(gl.GL_TEXTURE_2D, self.texture)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP_TO_BORDER)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP_TO_BORDER)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)

        w, h, *_ = IMAGE.shape # TODO: Texture class to store image and size

        gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGB, w, h, 0, gl.GL_RGB, gl.GL_UNSIGNED_BYTE, IMAGE)
        

        # Unbind the VAO and VBO to avoid accidental changes
        self.vertex_array.unbind()
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0) # Unbind the VBO

    def _create_vertex_buffer(self) -> VertexSpecification:
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

    def get_bounding_box(self) -> Rect2:
        '''
        Returns the bounding box of the element with scale, rotation and translation applied
        '''
        vertices = self._get_bounding_box_vertices()
        # Add forth dimension
        vertices = np.insert(vertices, 3, 0.0, axis=1)

        # Transform the vertices
        vertices = self.transform.model_matrix @ vertices.T

        # Find the minimum and maximum x and y values
        min_x = min(vertices, key=lambda x: x[0])[0]
        max_x = max(vertices, key=lambda x: x[0])[0]
        min_y = min(vertices, key=lambda x: x[1])[1]
        max_y = max(vertices, key=lambda x: x[1])[1]

        return Rect2(min_x, min_y, max_x, max_y) + self.transform.translation.xy

    def _get_bounding_box_vertices(self) -> np.ndarray:
        '''
        Return the bounding box of the element
        np.array([[x1, y1, z1], [x2, y2, z2], ...])
        '''
        raise NotImplementedError(f'{self.__class__.__name__} does not implement get_bounding_box')


    def _on_outside_screen(self):
        LOGGER.log_debug(f'{self.__class__.__name__} id={id(self)} is outside screen')
        self.destroy()

    def move_forward(self, intensity: float = 1.0):
        '''
        Move the element forward according to the current rotation
        '''
        dx = np.cos(self.angle + math.radians(90)) * intensity * self.speed
        dy = np.sin(self.angle + math.radians(90)) * intensity * self.speed
        self.transform.translation.xy += Vec2(dx, dy)


        

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
        If overriden in sublcass, must call super, updates the element's physics
        It is called every physics update (approx. 50 times per second)
        '''

        self_rect = self.get_bounding_box()
        if not SCREEN_RECT.intersects(self_rect): #TODO: check only when movement is made (to avoid overload of the CPU)
            self._on_outside_screen()

    def update(self):
        '''
        Updates the element, called every frame.
        If overridden, make sure to call the super method.
        Not intended to be overridden.
        '''
        if self.destroyed:
            LOGGER.log_warning(f'Trying to update destroyed element {self}')
            return

        if (delta_time := time.time() - self._last_physics_update) > 1/50:
            self._physics_update(delta_time)
            self._last_physics_update = time.time()

        if IS.is_pressed('t') and not self._was_t_pressed:
            LOGGER.log_warning('T pressed, but not implemented for now') #TODO: reimplement with new classes
            # self._vertex_specs = self._normal_vertex_specs if self._vertex_specs is self._ouline_vertex_specs else self._ouline_vertex_specs
            # gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.vbo)
            # gl.glBufferData(gl.GL_ARRAY_BUFFER, len(self._vertex_specs)*4, (gl.GLfloat * len(self._vertex_specs))(*self._vertex_specs), gl.GL_DYNAMIC_DRAW)
            # self._render_primitive = gl.GL_LINE_STRIP if self._render_primitive is gl.GL_TRIANGLES else gl.GL_TRIANGLES
        self._was_t_pressed = IS.is_pressed('t')

        self._render()
        
    def _render(self):
        '''
        Basic rendering method. Can be overridden in subclass.
        '''
        # Bind the shader and VAO (VBO is bound in the VAO)
        self.vertex_array.bind()
        self.vertex_buffer.bind()
        self.shader.use()

        gl.glBindTextureUnit(0, self.texture)

        # Set the transformation matrix
        self.shader.upload_uniform_matrix4f('u_Transformation', self.transform.model_matrix)
        # self.shader.upload_uniform_int('u_Texture', 0)
        # loc= gl.glGetUniformLocation(self.shader.program, 'u_Texture')
        # gl.glUniform1d(loc, gl.GL_TEXTURE0)

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
    
        # LOGGER.log_debug(f"{self} marked for destruction")
        self.__destroyed = True