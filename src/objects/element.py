from copy import copy, deepcopy
import dataclasses
import random
from turtle import Shape
import constants
from dataclasses import dataclass, field
import math
import time
from typing import TYPE_CHECKING, Union
import glm
import numpy as np

from OpenGL import GL as gl
from utils.geometry import Rect2, Vec2, Vec3
from utils.logger import LOGGER

import imageio
from gl_abstractions.texture import Texture, Texture2D, TextureParameters
from gl_abstractions.vertex_array import VertexArray
from gl_abstractions.vertex_buffer import VertexBuffer

from gl_abstractions.shader import Shader, ShaderDB
from wavefront.material import Material

from transform import Transform
from wavefront.model import Model

if TYPE_CHECKING:
    from objects._2d._2dworld import World


@dataclass
class ShapeSpec:
    '''
    Basic class that tore the vertices data of the object.
    It contains the vertices coordinates and its color
    '''
    vertices: np.ndarray
    indices: np.ndarray = None
    render_mode: int = field(default=gl.GL_TRIANGLES)
    shader: Shader = field(default_factory=lambda: ShaderDB.get_instance()[
                           'simple_red'])  # TODO: more readable way to do this?
    texture: Union[Texture, None] = field(default_factory=lambda: Texture2D.from_image_path('textures/white.jpg'))
    material: Material = field(default_factory=lambda: Material(f'default-{random.random()}'))
    name: str = 'Unnamed Shape'

    def __post_init__(self):
        assert self.texture is not None, f"Shape '{self.name}' has no texture"
        self.shader.layout.assert_data_ok(self.vertices)

@dataclass
class ShapeRenderer:
    '''
    Basic class that render the object, according to its vertices, texture, shader and primitive.
    '''
    shape_spec: ShapeSpec
    transform: Transform

    def __post_init__(self):
        self.shader = self.shape_spec.shader
        self.texture = self.shape_spec.texture
        self.shape_name = self.shape_spec.name

        self.vao = VertexArray()
        self.vao.bind()
        self.vbo = VertexBuffer(
            layout=self.shader.layout,
            data=self.shape_spec.vertices,
            usage=gl.GL_DYNAMIC_DRAW
        )
        # self.ibo = VertexBuffer(self.shape_spec.indices)
        self.vao.upload_vertex_buffer(self.vbo)

    def render(self):
        from app_vars import APP_VARS
        # Bind the shader and VAO (VBO is bound in the VAO)
        self.vao.bind()

        if self.texture is not None:
            self.texture.bind()

        self.shader.use()

        # gl.glBindTextureUnit(0, self.texture)

        # Calculate MVP
        mat_model = self.transform.model_matrix

        # def view(camera: Camera):
        camera = APP_VARS.camera
        mat_view = glm.lookAt(glm.vec3(*camera.transform.translation), glm.vec3(
            *camera.transform.translation) + camera.cameraFront, camera.cameraUp)
        mat_view = np.array(mat_view)
        # return mat_view

        # def projection():
        # perspective parameters: fovy, aspect, near, far
        mat_projection = glm.perspective(glm.radians(
            camera.fov), constants.WINDOW_SIZE[0]/constants.WINDOW_SIZE[1], 0.1, 1000.0)
        mat_projection = np.array(mat_projection)
        # return mat_projection

        # Set the transformation matrix
        try:
            self.shader.upload_uniform_matrix4f('u_Model', mat_model)
        except Exception as e:
            print(f'**********EXCEPTION WITH u_Model********')
            print(f'{mat_model=}')
            raise e
        try:
            self.shader.upload_uniform_matrix4f('u_View', mat_view) 
        except Exception as e:
            print(f'**********EXCEPTION WITH u_View********')
            print(f'{mat_view=}')
            raise e

        self.shader.upload_uniform_matrix4f('u_Projection', mat_projection)

        material = self.shape_spec.material

        self.shader.upload_uniform_vec3('u_Ka', material.Ka.values.astype(np.float32))
        self.shader.upload_uniform_vec3('u_Kd', material.Kd.values.astype(np.float32))
        self.shader.upload_uniform_vec3('u_Ks', material.Ks.values.astype(np.float32))
        self.shader.upload_uniform_float('u_Ns', material.Ns)
        self.shader.upload_uniform_float('u_d', material.d)

        self.shader.upload_uniform_vec3('u_GKa', Vec3(APP_VARS.lighting_config.Ka_x, APP_VARS.lighting_config.Ka_y, APP_VARS.lighting_config.Ka_z))
        self.shader.upload_uniform_vec3('u_GKd', Vec3(APP_VARS.lighting_config.Kd_x, APP_VARS.lighting_config.Kd_y, APP_VARS.lighting_config.Kd_z))
        self.shader.upload_uniform_vec3('u_GKs', Vec3(APP_VARS.lighting_config.Ks_x, APP_VARS.lighting_config.Ks_y, APP_VARS.lighting_config.Ks_z))
        self.shader.upload_uniform_float('u_GNs', APP_VARS.lighting_config.Ns)

        
        self.shader.upload_uniform_vec3('u_LightPos', APP_VARS.lighting_config.light_position.values.astype(np.float32) )
        self.shader.upload_uniform_vec3('u_CameraPos', APP_VARS.camera.transform.translation.values.astype(np.float32) )

        # Draw the vertices according to the primitive
        gl.glDrawArrays(self.shape_spec.render_mode, 0,
                        len(self.shape_spec.vertices))


@dataclass
class ElementSpecification:
    '''
    Basic class that holds the object basic data.
    '''
    initial_transform: Transform = field(default_factory=Transform)
    shape_specs: list[ShapeSpec] = field(default_factory=list)

    def __post_init__(self):
        # Ensure types are correct
        for shape in self.shape_specs:
            assert isinstance(
                shape, ShapeSpec), f'ShapeSpecs must be of type ShapeSpec, not {type(shape)}'
        assert isinstance(self.initial_transform,
                          Transform), f'initial_transform must be of type Transform, not {type(self.initial_transform)}'

    @staticmethod
    def from_model(model: Model, shader: Shader = None, texture = None) -> 'ElementSpecification':
        elspec = ElementSpecification()

        if shader is None:
            shader = ShaderDB.get_instance().get_shader('light_texture') # TODO: make shader part of the material

        if texture is None:
            texture = Texture2D.from_image_path('textures/white.jpg') # TODO: make texture part of something

        for object in model.objects:
            vertices_list = object.expand_faces_to_unindexed_vertices() # TODO: instead of unindexed, use indices
            material = object.material

            # assert material.name in ['Tree', 'Leaves'], f'{material.name}'

            has_position = 'a_Position' in [ attr[0] for attr in shader.layout.attributes]
            has_texcoord = 'a_TexCoord' in [ attr[0] for attr in shader.layout.attributes]
            has_normal = 'a_Normal' in [ attr[0] for attr in shader.layout.attributes]

            # # TODO: rename this variable to something less confusing
            vertices_array = np.array([
                # Example Vertex: (posX, posY, posZ, texU, texV, normX, normY, normZ)
                vertex.to_tuple(has_position, has_texcoord, has_normal) for vertex in vertices_list
            ], dtype=np.float32)

            object_shape = ShapeSpec(
                vertices=vertices_array,
                # indices= TODO: use indices,
                shader=shader,
                render_mode=gl.GL_TRIANGLES,
                name=f'{object.name}',
                texture=texture,
                material=material
            )
            elspec.shape_specs.append(object_shape)

        return elspec

@dataclass
class BoundingBox2DCache:
    '''
    Class that defines the boundaries (hitbox) of all its children classes
    '''
    _bounding_box: Rect2 = None

    _last_vertices: np.ndarray = None
    _last_model_matrix: np.ndarray = None

    def get_bounding_box(self, vertices_4d: np.ndarray, model_matrix: np.ndarray) -> Rect2:
        if self._last_vertices is not None and self._bounding_box is not None and np.array_equal(self._last_vertices, vertices_4d) and np.array_equal(self._last_model_matrix, model_matrix):
            return self._bounding_box

        self._bounding_box = self._calculate_bounding_box(
            vertices_4d, model_matrix)
        self._last_model_matrix = model_matrix

        return self._bounding_box

    def _calculate_bounding_box(self, vertices_4d: np.ndarray, model_matrix: np.ndarray) -> Rect2:
        # Transform the vertices
        tranformed_vertices = (model_matrix @ vertices_4d.T).T

        # Find the minimum and maximum x and y values
        min_x = min(tranformed_vertices, key=lambda x: x[0])[0]
        max_x = max(tranformed_vertices, key=lambda x: x[0])[0]
        min_y = min(tranformed_vertices, key=lambda x: x[1])[1]
        max_y = max(tranformed_vertices, key=lambda x: x[1])[1]

        return Rect2(min_x, min_y, max_x, max_y)


@dataclass
class PhysicsState:
    last_tick_time: float = field(default_factory=lambda: time.time())


@dataclass
class ObjectState:
    physics_state: PhysicsState = field(default_factory=PhysicsState)
    destroyed = False
    selected = False  # TODO: remove debug or refactor


PHYSICS_TPS = 50  # TODO: move to Physics System when it's done


@dataclass
class Element: # TODO: rename to Object
    name: str
    shape_specs: list[ShapeSpec]
    transform: Transform = field(default_factory=Transform)
    ray_selectable: bool = True
    ray_destroyable: bool = True

    def __post_init__(self):
        assert isinstance(self.shape_specs, list), f"Expected 'shape_specs' to be a 'list[ShapeSpec]', but got {type(self.shape_specs)} instead"
        assert isinstance(self.transform, Transform), f"Expected 'transform' to be a 'Transform', but got {type(self.transform)} instead"
        
        self._state = ObjectState()
        self._shape_renderers = [
            ShapeRenderer(
                shape_spec=shape_spec,
                transform=self.transform
            ) for shape_spec in self.shape_specs]

        pass
    
    def on_spawned(self, world: 'World'):
        '''Please override'''
        pass

    @property
    def destroyed(self):
        return self._state.destroyed

    @property
    def center(self) -> Vec3:
        return self.transform.translation.xyz
    
    @property
    def pseudo_hitbox_distance(self) -> float:
        return self.transform.scale.magnitude()

    def destroy(self):
        if self.destroyed:
            # raise RuntimeError(f'Trying to destroy already destroyed element {self}')
            LOGGER.log_warning(
                f'Trying to destroy already destroyed element {self.name=}, {type(self)=}, {self.transform.translation=}')
            return

        # LOGGER.log_debug(f"{self} marked for destruction")
        self._state.destroyed = True

    def update(self, delta_time: float):
        '''Receives a tick every frame'''
        self._try_update_physics()
        self._render(delta_time=delta_time)
        pass

    def select(self) -> None:
        if self._state.selected:
            return
        self._state.selected = True
        # self.transform.scale *= 2

        self._old_materials = []
        for shape in self.shape_specs:
            self._old_materials.append(shape.material)
            curr_mat = deepcopy(shape.material)
            shape.material = curr_mat
            curr_mat.Kd[0] = 3
            curr_mat.Ka[0] = 3
            curr_mat.Ks[0] = 3

        return # TODO: make a proper selection shader
        self._old_shaders = []
        for renderer in self._shape_renderers:
            self._old_shaders.append(renderer.shader)
            renderer.shader = ShaderDB.get_instance().get_shader('simple_red')

    def unselect(self) -> None:
        if not self._state.selected:
            return
        self._state.selected = False
        # self.transform.scale /= 2

        for idx, shape in enumerate(self.shape_specs):
            shape.material = self._old_materials[idx]

        return # TODO: make a proper selection shader
        for renderer, old_shader in zip(self._shape_renderers, self._old_shaders):
            renderer.shader = old_shader
            
        self._old_shaders = []
    def _try_update_physics(self):
        if (delta_time := time.time() - self._state.physics_state.last_tick_time) > 1/PHYSICS_TPS:
            self._state.physics_state.last_tick_time = time.time()
            self._physics_update(delta_time)

    def _physics_update(self, delta_time: float):
        '''Receives a tick every physics frame (around 50TPS)'''
        pass

    def _render(self, delta_time: float):
        for renderer in self._shape_renderers:
            renderer.render()

    def __repr__(self) -> str:
        '''
        Return a string representation of the element
        '''
        return f'{self.__class__.__name__}(id={str(id(self))[-5:]}, x={self.x}, y={self.y}, z={self.z})'


    pass


# class Element:
#     '''
#     Basic class that derives all the others ones in the world.
#     Responsible for defining their size, behavior (translarion, rotation, scale),
#     rendering, update and boundaries
#     '''

#     def __init__(self, world: 'World', specs: ElementSpecification):
#         '''
#         Initialize the element inside the world, with an optional initial transform
#         '''
#         from objects.world import World
#         assert isinstance(
#             world, World), f'Expected world to be a World, got {type(world)} instead'
#         assert isinstance(
#             specs, ElementSpecification), f'Expected specs to be a ElementSpecification, got {type(specs)} instead'

#         self._transform = specs.initial_transform
#         self.primitives = specs.shape_specs

#         self._last_physics_update = time.time()  # Used for physics updates
#         self.__destroyed = False
#         self._dying = False
#         self._selected = False

#         # Take all shapes specified in specs and create a list of ShapeRenderers to render them later
#         self.shape_renderers = [
#             ShapeRenderer(shape_spec, self.transform) for shape_spec in specs.shape_specs
#         ]

#     def select(self) -> None:
#         if self._selected:
#             return
#         self._selected = True
#         self.transform.translation += 10

#     def unselect(self) -> None:
#         if not self._selected:
#             return
#         self._selected = False
#         self.transform.translation -= 10

#     def die(self):
#         '''Set the element to start a death animation'''
#         self._dying = True

#     def _physics_update(self, delta_time: float):
#         '''
#         If overriden in sublcass, must call super, updates the element's physics
#         It is called every physics update (approx. 50 times per second)
#         '''

#         # try:
#         #     self_rect = self.get_bounding_box_2d()
#         #     if not SCREEN_RECT.intersects(self_rect): #TODO: check only when movement is made (to avoid overload of the CPU)
#         #         self._on_outside_screen()
#         # except NotImplementedError:
#         #     LOGGER.log_trace(f'{self.__class__.__name__} does not implement get_bounding_box, skipping outside screen check', self.__class__)
#         #     pass

#     def update(self, delta_time: float):
#         '''
#         Updates the element, called every frame.
#         If overridden, make sure to call the super method.
#         Not intended to be overridden.
#         '''
#         if self.destroyed:
#             LOGGER.log_warning(f'Trying to update destroyed element {self}')
#             return

#         # TODO: move this to world? world is already processing update's delta_time, so why should element calculate physics delta_time?
#         if (delta_time := time.time() - self._last_physics_update) > 1/50:
#             self._physics_update(delta_time)
#             self._last_physics_update = time.time()

#         self._render()

#     def _render(self):
#         '''
#         Basic rendering method. Can be overridden in subclass.
#         '''

#         # Death animation
#         if self._dying:
#             self.transform.scale *= 0.9
#             if self.transform.scale.x < 0.1:
#                 self.destroy()
#                 return

#         # Render all the shapes
#         for shape_renderer in self.shape_renderers:
#             shape_renderer.render()

#         # Render the bounding box (if enabled)
#         self._render_debug()

#     def _render_debug(self):
#         '''
#         Renders debug information about the element if enabled.
#         '''
#         from app_vars import APP_VARS
#         if APP_VARS.debug.show_bbox:
#             try:
#                 # Create a new shape renderer for the bounding box (uses CPU to compute the bounding box and transform its vertices)
#                 min_x, min_y, max_x, max_y = self.get_bounding_box_2d()
#                 bounding_box_renderer = ShapeRenderer(
#                     transform=Transform(),
#                     shape_spec=ShapeSpec(
#                         vertices=np.array([
#                             [*(min_x, min_y, 0.0), *(1, 0, 1)],
#                             [*(max_x, min_y, 0.0), *(1, 0, 1)],

#                             [*(max_x, min_y, 0.0), *(1, 0, 1)],
#                             [*(max_x, max_y, 0.0), *(1, 0, 1)],

#                             [*(max_x, max_y, 0.0), *(1, 0, 1)],
#                             [*(min_x, max_y, 0.0), *(1, 0, 1)],

#                             [*(min_x, max_y, 0.0), *(1, 0, 1)],
#                             [*(min_x, min_y, 0.0), *(1, 0, 1)],
#                         ], dtype=np.float32),
#                         shader=ShaderDB.get_instance().get_shader('colored'),
#                         render_mode=gl.GL_LINES,
#                     ),
#                 )
#                 bounding_box_renderer.render()
#             except NotImplementedError:
#                 # If the element does not implement get_bounding_box, we cannot render the bounding box
#                 # So we just ignore it
#                 pass

#     @property
#     def destroyed(self):
#         '''
#         Returns whether the element is destroyed or not
#         '''
#         return self.__destroyed

#     def destroy(self):
#         '''
#         Destroys the element
#         '''
#         if self.destroyed:
#             # raise RuntimeError(f'Trying to destroy already destroyed element {self}')
#             LOGGER.log_warning(
#                 f'Trying to destroy already destroyed element {self}')
#             return

#         # LOGGER.log_debug(f"{self} marked for destruction")
#         self.__destroyed = True

#     # def get_bounding_box_2d(self) -> Rect2:
#     #     '''
#     #     Returns the bounding box of the element with scale, rotation and translation applied
#     #     '''
#     #     return self._bounding_box_cache.get_bounding_box(self._bounding_box_vertices_4d, self.transform.model_matrix)

#     # def _generate_bounding_box_2d_vertices(self) -> np.ndarray:
#     #     '''
#     #     Return the bounding box of the element
#     #     np.array([[x1, y1, z1], [x2, y2, z2], ...])
#     #     '''
#     #     raise NotImplementedError(f'{self.__class__.__name__} does not implement _generate_bounding_box_vertices')

#     # TODO: what does this mean for 3D?
#     # def _on_outside_screen(self):
#     #     '''
#     #     Define what to do when the element is outside the screen
#     #     Can be overridden in subclass
#     #     '''
#     #     LOGGER.log_debug(f'{self.__class__.__name__} id={id(self)} is outside screen')
#     #     self.destroy()

#     # def move_forward(self, intensity: float = 1.0):
#     #     '''
#     #     Move the element forward according to the current rotation
#     #     '''
#     #     dx = np.cos(self.angle + math.radians(90)) * intensity * self.speed
#     #     dy = np.sin(self.angle + math.radians(90)) * intensity * self.speed
#     #     self.transform.translation.xy += Vec2(dx, dy)

#     @property
#     def transform(self) -> Transform:
#         '''
#         Returns the transform of the element
#         '''
#         return self._transform

#     @property
#     def x(self):
#         '''
#         Get the x coordinate of the element
#         '''
#         return self.transform.translation.x

#     @x.setter
#     def x(self, value: float):
#         '''
#         Set the x coordinate of the element
#         '''
#         self.transform.translation.x = value

#     @property
#     def y(self):
#         '''
#         Get the y coordinate of the element
#         '''
#         return self.transform.translation.y

#     @y.setter
#     def y(self, value: float):
#         '''
#         Set the y coordinate of the element
#         '''
#         self.transform.translation.y = value

#     @property  # No setter, because it's a read-only property (2D only)
#     def z(self):
#         '''
#         Get the z coordinate of the element (no setter available, since we're in 2D)
#         '''
#         return self.transform.translation.z

#     @z.setter
#     def z(self, value: float):
#         '''
#         Set the z coordinate of the element
#         '''
#         self.transform.translation.z = value

#     # @property
#     # def angle(self):
#     #     '''
#     #     Get the angle of the element on the Z axis
#     #     '''
#     #     return self.transform.rotation.z

#     # @angle.setter
#     # def angle(self, value: float):
#     #     '''
#     #     Set the angle of the element on the Z axis
#     #     '''
#     #     self.transform.rotation.z = value

#     def __repr__(self) -> str:
#         '''
#         Return a string representation of the element
#         '''
#         return f'{self.__class__.__name__}(id={str(id(self))[-5:]}, x={self.x}, y={self.y}, z={self.z})'
