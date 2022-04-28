from dataclasses import dataclass, field
import math
import time
from typing import TYPE_CHECKING, Union
import numpy as np

from OpenGL import GL as gl
from utils.geometry import Rect, Rect2, Vec2, Vec3
from utils.logger import LOGGER
from constants import FLOAT_SIZE, SCREEN_RECT

import imageio
from gl_abstractions.texture import Texture2D, Texture2DParameters
from gl_abstractions.vertex_array import VertexArray
from gl_abstractions.vertex_buffer import VertexBuffer

from gl_abstractions.shader import Shader, ShaderDB

from transform import Transform

TEXTURED_SHADER = None
IMAGE: imageio.core.util.Array = np.array(imageio.imread('./textures/enemy_texture.jpg')[::-1,:,:]) # TODO: relative path

from input.input_system import INPUT_SYSTEM as IS

if TYPE_CHECKING:
    from world import World

@dataclass
class ShapeSpec:
    vertices: np.ndarray
    indices: np.ndarray = None
    render_mode: int = field(default=gl.GL_TRIANGLES)
    shader: Shader = field(default_factory=lambda: ShaderDB.get_instance()['simple_red']) # TODO: more readable way to do this?
    texture: Union[Texture2D, None] = None
    name: str = 'Unnamed Shape'

    def __post_init__(self):
        # TODO: add shader.needs_texture() (or something)
        needs_texture = self.shader is ShaderDB.get_instance()['textured']
        if needs_texture:
            assert self.texture is not None, f"Shape '{self.name}' has no texture, but specified shader requires one {self.shader=}"


@dataclass
class ShapeRenderer:
    shape_spec: ShapeSpec
    transform: Transform

    def __post_init__(self):
        self.shader = self.shape_spec.shader
        self.texture = self.shape_spec.texture
        self.shape_name = self.shape_spec.name

        self.vao = VertexArray()
        self.vao.bind()
        self.vbo = VertexBuffer(self.shape_spec.vertices, usage=gl.GL_DYNAMIC_DRAW)
        self.vbo.bind()
        # self.ibo = VertexBuffer(self.shape_spec.indices)

        self.vao.apply_layout(self.shape_spec.shader.layout)

    def render(self):
        # Bind the shader and VAO (VBO is bound in the VAO)
        self.vao.bind()

        if self.texture is not None:
            self.texture.bind()
        
        self.shader.use()

        # gl.glBindTextureUnit(0, self.texture)

        # Set the transformation matrix
        self.shader.upload_uniform_matrix4f('u_Transformation', self.transform.model_matrix)

        # Draw the vertices according to the primitive
        gl.glDrawArrays(self.shape_spec.render_mode, 0, len(self.shape_spec.vertices))

@dataclass
class ElementSpecification:
    initial_transform: Transform = field(default_factory=Transform)
    shape_specs: list[ShapeSpec] = field(default_factory=list)

    def __post_init__(self):
        # Ensure types are correct
        for shape in self.shape_specs:
            assert isinstance(shape, ShapeSpec), f'ShapeSpecs must be of type ShapeSpec, not {type(shape)}'
        assert isinstance(self.initial_transform, Transform), f'initial_transform must be of type Transform, not {type(self.initial_transform)}'

class Element:
    '''
    An abstract class for all the elements in the game
    '''

    def __init__(self, world: 'World', specs: ElementSpecification):
        '''
        Initialize the element inside the world, with an optional initial transform
        '''
        from world import World
        assert isinstance(world, World), f'{world} is not a World'
        assert isinstance(specs, ElementSpecification), f'{specs} is not an Elementspecs'

        self._transform = specs.initial_transform
        self.primitives = specs.shape_specs
    
        self.world = world
        world.spawn(self)

        self._last_physics_update = time.time() # Used for physics updates
        self.__destroyed = False
        self.speed = 0.5

        self.shape_renderers = [
            ShapeRenderer(shape_spec, self.transform) for shape_spec in specs.shape_specs
        ]

        print(f'Type of IMAGE: {type(IMAGE)}')

        # self.texture = Texture2D(Texture2DParameters())
        # self.texture.upload_raw_texture(IMAGE)

        # self.texture_CHANGEME = gl.glGenTextures(1) # TODO: generate once per different element (self._create_texture)
        # LOGGER.log_debug(f'{self.__class__.__name__} id={id(self)} texture id={self.texture_CHANGEME}')

        # gl.glBindTexture(gl.GL_TEXTURE_2D, self.texture_CHANGEME)
        # gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP_TO_BORDER)
        # gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP_TO_BORDER)
        # gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
        # gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)

        # w, h, *_ = IMAGE.shape # TODO: Texture class to store image and size

        # gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGB, w, h, 0, gl.GL_RGB, gl.GL_UNSIGNED_BYTE, IMAGE)
        
    def DEPRECATED_USE_SPECS_IN_CONSTRUCTOR(self):
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
        vertices = np.insert(vertices, 3, 1.0, axis=1)
        # vertices 

        # Transform the vertices
        vertices = (self.transform.model_matrix @ vertices.T).T

        # Find the minimum and maximum x and y values
        min_x = min(vertices, key=lambda x: x[0])[0]
        max_x = max(vertices, key=lambda x: x[0])[0]
        min_y = min(vertices, key=lambda x: x[1])[1]
        max_y = max(vertices, key=lambda x: x[1])[1]

        return Rect2(min_x, min_y, max_x, max_y)

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
    def transform(self) -> Transform:
        '''
        Returns the transform of the element
        '''
        return self._transform

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

        try:
            self_rect = self.get_bounding_box()
            if not SCREEN_RECT.intersects(self_rect): #TODO: check only when movement is made (to avoid overload of the CPU)
                self._on_outside_screen()
        except NotImplementedError:
            LOGGER.log_trace(f'{self.__class__.__name__} does not implement get_bounding_box, skipping outside screen check', self.__class__)
            pass

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

        self._render()
        
    def _render(self):
        '''
        Basic rendering method. Can be overridden in subclass.
        '''
        for shape_renderer in self.shape_renderers:
            shape_renderer.render()

        self._render_debug()        

    def _render_debug(self):
        '''
        Renders the element in debug mode
        '''
        from app_vars import APP_VARS
        if APP_VARS.debug.show_bbox:
            try:
                min_x, min_y, max_x, max_y = self.get_bounding_box()
                bounding_box_renderer = ShapeRenderer(
                        transform=Transform(),
                        shape_spec=ShapeSpec(
                            vertices=np.array([
                                *( min_x, min_y, 0.0), *(1, 0, 1),
                                *( max_x, min_y, 0.0), *(1, 0, 1),

                                *( max_x, min_y, 0.0), *(1, 0, 1),
                                *( max_x, max_y, 0.0), *(1, 0, 1),

                                *( max_x, max_y, 0.0), *(1, 0, 1),
                                *( min_x, max_y, 0.0), *(1, 0, 1),
                                
                                *( min_x, max_y, 0.0), *(1, 0, 1),
                                *( min_x, min_y, 0.0), *(1, 0, 1),
                            ], dtype=np.float32),
                            shader=ShaderDB.get_instance().get_shader('colored'),
                            render_mode=gl.GL_LINES,
                        ),
                    )
                bounding_box_renderer.render()
            except NotImplementedError:
                pass
            

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