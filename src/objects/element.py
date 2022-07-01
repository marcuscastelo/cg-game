from copy import deepcopy
import random
import constants
from dataclasses import dataclass, field
import time
from typing import TYPE_CHECKING, Union
import glm
import numpy as np

from OpenGL import GL as gl
from utils.geometry import Rect2, Vec3
from utils.logger import LOGGER

from gl_abstractions.texture import Texture
from gl_abstractions.vertex_array import VertexArray
from gl_abstractions.vertex_buffer import VertexBuffer

from gl_abstractions.shader import Shader, ShaderDB
from wavefront.material import Material

from transform import Transform
from wavefront.model import Model

if TYPE_CHECKING:
    from objects.world import World

# TODO: move classes out of this file (too many lines)

@dataclass
class ShapeSpec:
    '''
    Basic class that store the vertices data of the object.
    It contains the vertices coordinates and its color
    '''
    vertices: np.ndarray
    indices: np.ndarray = None
    render_mode: int = field(default=gl.GL_TRIANGLES)
    shader: Shader = field(default_factory=lambda: ShaderDB.get_instance()[
                           'simple_red'])  # TODO: more readable way to do this?
    texture: Union[Texture, None] = None
    material: Material = field(
        default_factory=lambda: Material(f'default-{random.random()}'))
    name: str = 'Unnamed Shape'

    def __post_init__(self):
        self.shader.layout.assert_data_ok(self.vertices)


@dataclass
class ShapeRenderer:
    '''
    Basic class that renders the object, according to its vertices, texture, shader and primitive.
    '''
    element_name: str
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
        # TODO: refactor and comment this (maybe Shader.upload_uniforms()? no idea)
        from app_vars import APP_VARS
        # Bind the shader and VAO (VBO is bound in the VAO)
        self.vao.bind()

        if self.texture is not None:
            self.texture.bind()

        self.shader.use()

        # gl.glBindTextureUnit(0, self.texture)

        # Calculate MVP

        # Model
        mat_model = self.transform.model_matrix

        # View
        camera = APP_VARS.camera
        # TODO: stop using glm for that (assignment requisite)
        mat_view = glm.lookAt(glm.vec3(*camera.transform.translation), glm.vec3(
            *camera.transform.translation) + camera.cameraFront, camera.cameraUp)
        mat_view = np.array(mat_view)

        # Projection
        # TODO: stop using glm for that (assignment requisite)
        mat_projection = glm.perspective(glm.radians(
            camera.fov), constants.WINDOW_SIZE[0]/constants.WINDOW_SIZE[1], 0.1, 1000.0)
        mat_projection = np.array(mat_projection)

        # Upload MVP Matrices
        # TODO: only upload if changed (to increase performance)
        self.shader.upload_uniform_matrix4f('u_Model', mat_model)
        self.shader.upload_uniform_matrix4f('u_View', mat_view)
        self.shader.upload_uniform_matrix4f('u_Projection', mat_projection)

        # Upload Material Properties
        material = self.shape_spec.material

        self.shader.upload_uniform_vec3(
            'u_Ka', material.Ka.values.astype(np.float32))
        self.shader.upload_uniform_vec3(
            'u_Kd', material.Kd.values.astype(np.float32))
        self.shader.upload_uniform_vec3(
            'u_Ks', material.Ks.values.astype(np.float32))
        self.shader.upload_uniform_float('u_Ns', material.Ns)
        self.shader.upload_uniform_float('u_d', material.d)

        # Upload Global Lighting Properties
        # TODO: only upload if changed (to increase performance)
        self.shader.upload_uniform_vec3('u_GKa', Vec3(
            APP_VARS.lighting_config.Ka_x, APP_VARS.lighting_config.Ka_y, APP_VARS.lighting_config.Ka_z))
        self.shader.upload_uniform_vec3('u_GKd', Vec3(
            APP_VARS.lighting_config.Kd_x, APP_VARS.lighting_config.Kd_y, APP_VARS.lighting_config.Kd_z))
        self.shader.upload_uniform_vec3('u_GKs', Vec3(
            APP_VARS.lighting_config.Ks_x, APP_VARS.lighting_config.Ks_y, APP_VARS.lighting_config.Ks_z))
        self.shader.upload_uniform_float('u_GNs', APP_VARS.lighting_config.Ns)

        # Upload light sources positions
        if APP_VARS.last_bullet:
            self.shader.upload_uniform_vec3(
                'u_BulletPos', APP_VARS.last_bullet.transform.translation.values.astype(np.float32))
        else:
            self.shader.upload_uniform_vec3('u_BulletPos',  Vec3(
                0, -1000, 0).values.astype(np.float32))

        self.shader.upload_uniform_vec3(
            'u_AuxRobotPos', APP_VARS.lighting_config.light_position.values.astype(np.float32))

        # Upload Camera Position
        self.shader.upload_uniform_vec3(
            'u_CameraPos', APP_VARS.camera.transform.translation.values.astype(np.float32))

        # Upload bool to know if the shape should try to read a texture
        self.shader.upload_bool('u_HasTexture', int(self.texture is not None))

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
    def from_model(model: Model, shader: Shader = None, texture=None) -> 'ElementSpecification':
        ''' Create an ElementSpecification from a model. '''
        elspec = ElementSpecification()

        if shader is None:
            shader = ShaderDB.get_instance().get_shader(
                'light_texture')  # TODO: make shader part of the material?

        for object in model.objects:
            # TODO: instead of unindexed, use indices (make a GUI option)
            vertices_list = object.expand_faces_to_unindexed_vertices()
            material = object.material

            # assert material.name in ['Tree', 'Leaves'], f'{material.name}'

            has_position = 'a_Position' in [attr[0]
                                            for attr in shader.layout.attributes]
            has_texcoord = 'a_TexCoord' in [attr[0]
                                            for attr in shader.layout.attributes]
            has_normal = 'a_Normal' in [attr[0]
                                        for attr in shader.layout.attributes]

            # # TODO: rename this variable to something less confusing
            vertices_array = np.array([
                # Example Vertex: (posX, posY, posZ, texU, texV, normX, normY, normZ)
                vertex.to_tuple(has_position, has_texcoord, has_normal) for vertex in vertices_list
            ], dtype=np.float32)

            if len(vertices_array.shape) == 2:
                object_shape = ShapeSpec(
                    vertices=vertices_array,
                    # indices= # TODO: use indices (if GUI option is enabled),
                    shader=shader,
                    render_mode=gl.GL_TRIANGLES,
                    name=f'{object.name}',
                    texture=texture,
                    material=material
                )
                elspec.shape_specs.append(object_shape)
            else:
                LOGGER.log_warning(
                    f'Object or Group {model.name}::{object.name} has weird shape {vertices_array.shape}')

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
    ''' Class that defines the physics state of an object. '''
    last_tick_time: float = field(default_factory=lambda: time.time())
    # TODO: add momentum and velocity here
    # TODO: collision system
    # TODO: physics material? probably not here


@dataclass
class ElementState:
    physics_state: PhysicsState = field(default_factory=PhysicsState)
    destroyed = False
    selected = False  # TODO: remove debug or refactor


PHYSICS_TPS = 50  # TODO: move to Physics System when it's done


@dataclass
class Element:
    ''' Element class that holds the data of a single object in the scene. '''
    name: str
    # TODO: use ElementSpecification
    shape_specs: list[ShapeSpec]
    transform: Transform = field(default_factory=Transform)
    ray_selectable: bool = True
    ray_destroyable: bool = True

    def __post_init__(self):
        ''' Initialize the element. '''
        assert isinstance(
            self.shape_specs, list), f"Expected 'shape_specs' to be a 'list[ShapeSpec]', but got {type(self.shape_specs)} instead"
        assert isinstance(
            self.transform, Transform), f"Expected 'transform' to be a 'Transform', but got {type(self.transform)} instead"

        self._state = ElementState()
        self._shape_renderers = [
            ShapeRenderer(
                element_name=self.name,
                shape_spec=shape_spec,
                transform=self.transform
            ) for shape_spec in self.shape_specs]

        pass

    def on_spawned(self, world: 'World'):
        ''' Virtual method that is called when the element is spawned in the world. '''
        pass

    @property
    def destroyed(self):
        ''' Returns whether the element is destroyed or not. '''
        return self._state.destroyed

    @property
    def center(self) -> Vec3:
        ''' Returns the center of the element (some models have its vertices centered around 0,0,0, but this is not the case for all models). '''
        return self.transform.translation.xyz

    @property
    def pseudo_hitbox_distance(self) -> float:
        ''' Instead of using the bounding box, use the distance between the center of the elements to check if the element is hit. '''
        return self.transform.scale.magnitude()

    def destroy(self):
        if self.destroyed:
            LOGGER.log_warning(
                f'Trying to destroy already destroyed element {self.name=}, {type(self)=}, {self.transform.translation=}')
            return

        # The world will remove the element from the list of elements
        self._state.destroyed = True

    def update(self, delta_time: float):
        ''' Virtual method that is called every frame. '''
        self._try_update_physics()
        self._render(delta_time=delta_time)
        pass

    def select(self) -> None:
        ''' Virtual method that is called when the element is selected. '''
        if self._state.selected:
            return

        self._state.selected = True

        # Change element material to a new one (red in all light types)
        self._old_materials = []
        for shape in self.shape_specs:
            self._old_materials.append(shape.material)
            curr_mat = deepcopy(shape.material)
            shape.material = curr_mat
            curr_mat.Kd[0] = 3
            curr_mat.Ka[0] = 3
            curr_mat.Ks[0] = 3

    def unselect(self) -> None:
        ''' Virtual method that is called when the element is unselected. '''
        if not self._state.selected:
            return
        self._state.selected = False

        # Change back the material to the old one
        for shape, material in zip(self.shape_specs, self._old_materials):
            shape.material = material

    def _try_update_physics(self):
        ''' Every frame, check if it's time to update the physics, and if so, update it. '''
        if (delta_time := time.time() - self._state.physics_state.last_tick_time) > 1/PHYSICS_TPS:
            self._state.physics_state.last_tick_time = time.time()
            self._physics_update(delta_time)

    def _physics_update(self, delta_time: float):
        ''' Virtual method that is called every physics frame (around 50TPS) to update the physics. '''
        pass

    def _render(self, delta_time: float):
        ''' Virtual method that is called every frame to render the element. '''
        for renderer in self._shape_renderers:
            renderer.render()

    def __repr__(self) -> str:
        ''' Return a string representation of the element '''
        return f'{self.__class__.__name__}(id={str(id(self))[-5:]}, x={self.x}, y={self.y}, z={self.z})'