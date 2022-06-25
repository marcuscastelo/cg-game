from dataclasses import dataclass, field
from itertools import accumulate
import math
from turtle import shape
import glm
from utils.geometry import Vec3
from utils.sig import metsig
import constants
import glfw
from gl_abstractions.shader import ShaderDB
from line import Line

from objects.element import PHYSICS_TPS, Element, ElementSpecification, ShapeSpec
from objects.physics.momentum import Momentum
from objects.world import World
from ray import Ray
from transform import Transform

from input.input_system import INPUT_SYSTEM as IS



@dataclass
class Camera(Element):
    shape_specs: list[ShapeSpec] = field(default_factory=list)
    fov = 70
    _sprinting = False

    def __post_init__(self):
        super().__post_init__()
        self._momentum = Momentum()

        # self.cameraPos   = glm.vec3(0.0,  0.0,  1.0)
        self.cameraFront = glm.vec3(0.0,  0.0, -1.0)
        self.cameraUp    = glm.vec3(0.0,  1.0,  0.0)
        self.cameraSpeed = 2

        self.yaw = 0.0
        self.pitch = 0.0

        self._keyboardMovementInput = glm.vec3(0, 0, 0)
        
        self._fall_speed = 0
        self._ground_y = 1.8

        self.raycast_line_dbg: Line = None
        self.ray: Line = None

    def on_spawned(self, world: 'World'):
        self.raycast_line_dbg = Line('test_line', shader=ShaderDB.get_instance().get_shader('simple_blue'))
        self.raycast_line_dbg.transform.scale.z = 10
        # world.spawn(self.raycast_line_dbg)
        return super().on_spawned(world)

    @property
    def cameraRight(self):
        return glm.normalize(glm.cross(self.cameraFront, self.cameraUp))

    @property
    def grounded(self):
        return self.transform.translation.y <= self._ground_y * 1.01

    def reset(self):
        new_camera = Camera(self.name)
        for attr in self.__dict__.keys():
            setattr(self, attr, getattr(new_camera, attr))

    def update(self, delta_time: float):
        self.raycast_line_dbg.transform.translation.xz = self.transform.translation.xz
        self.raycast_line_dbg.transform.translation.y = self._ground_y - 0.05
        self.raycast_line_dbg.transform.rotation.xyz = self.transform.rotation.xyz

        if IS.just_pressed('ctrl') and Vec3(*self._keyboardMovementInput).magnitude() > 0:
            self._sprinting = True
            self._momentum.max_speed = 0.2
            self._momentum.accel = 0.1
        if IS.just_released('ctrl') or Vec3(*self._keyboardMovementInput).magnitude() <= 0.01:
            self._sprinting = False
            self._momentum.max_speed = 0.1
            self._momentum.accel = 0.01

        if IS.just_pressed('shift') and Vec3(*self._keyboardMovementInput).magnitude() > 0:
            self._ground_y = 1.6
        if IS.just_released('shift') or Vec3(*self._keyboardMovementInput).magnitude() <= 0.01:
            self._ground_y = 1.8

        fov_delta_sig = +1 if self._sprinting else -1
        self.fov += fov_delta_sig * delta_time * 60 * 1.5
        if self.fov < 70: self.fov = 70
        elif self.fov > 90: self.fov = 90

        super().update(delta_time)
        pass

    def on_key(self, window, key: int, scancode, action: int, mods):
        # TODO: remove debug
        from app_vars import APP_VARS
        rays: list[Ray] = list(filter(lambda e: isinstance(e, Ray), APP_VARS.world.elements))
        if rays:
            if IS.just_pressed('r'):
                rays[0].transform.translation.xyz = self.transform.translation.xyz
                rays[0].direction = Vec3(*APP_VARS.camera.cameraFront).normalized()


        # TODO: refactor to use forces
        positive_actions = [ glfw.PRESS ]
        negative_actions = [ glfw.RELEASE ]

        if key == glfw.KEY_LEFT_CONTROL:
            if action in positive_actions:
                self.cameraSpeed *= 2
            else:
                self.cameraSpeed /= 2

            return

        direction_vecs = {
            'front':    glm.vec3(+1, 0, 0),
            'back':     glm.vec3(-1, 0, 0),
            'right':    glm.vec3(0, 0, +1),
            'left':     glm.vec3(0, 0, -1),
            'up':       glm.vec3(0, +10, 0),
            'down':     glm.vec3(0, -1, 0),
        }

        keymap = {
            glfw.KEY_W: 'front',
            glfw.KEY_S: 'back',
            glfw.KEY_A: 'left',
            glfw.KEY_D: 'right',
            glfw.KEY_SPACE: 'up',
            glfw.KEY_LEFT_SHIFT: 'down'
        }

        for keyname, direction in keymap.items():
            direction_vec = direction_vecs[direction]
            if key == keyname:
                if action in positive_actions:
                    self._keyboardMovementInput += direction_vec 
                if action in negative_actions:
                    self._keyboardMovementInput -= direction_vec 


        # if key == glfw.KEY_SPACE and action == glfw.PRESS:
        #     if self.grounded:
        #         self._keyboardMovementInput += glm.vec3(0, 1, 0)
        # if key == glfw.KEY_SPACE and action in [glfw.REPEAT, glfw.RELEASE]:
        #     if not self.grounded:
        #         self._keyboardMovementInput.y = 0


    def _rotate_vec_to_face_front(self, vec: glm.vec3) -> glm.vec3:
        aligned_vec = vec
        aligned_vec = glm.rotateY(aligned_vec, math.radians(-self.yaw))
        return aligned_vec

    def on_cursor_pos(self, window, xpos, ypos):
        from app_vars import APP_VARS

        # if APP_VARS.cursor.lastX == None or APP_VARS.cursor.lastY == None:
        #     # Do not move camera if mouse just returned from pause screen
        #     APP_VARS.cursor.lastX = xpos
        #     APP_VARS.cursor.lastY = ypos    

        if APP_VARS.cursor.lastX == None:
            APP_VARS.cursor.lastX = xpos

        if APP_VARS.cursor.lastY == None:
            APP_VARS.cursor.lastY = ypos

        xoffset = xpos - APP_VARS.cursor.lastX
        yoffset = APP_VARS.cursor.lastY - ypos
        APP_VARS.cursor.lastX = xpos
        APP_VARS.cursor.lastY = ypos

        sensitivity = 0.06 
        xoffset *= sensitivity
        yoffset *= sensitivity

        self.yaw += xoffset;
        self.pitch += yoffset;

        if self.pitch >= 90.0: self.pitch = 90.0
        if self.pitch <= -90.0: self.pitch = -90.0

        yaw = glm.radians(self.yaw)
        pitch = glm.radians(self.pitch)

        front = glm.vec3()
        front.x = math.cos(yaw) * math.cos(pitch)
        front.y = math.sin(pitch)
        front.z = math.sin(yaw) * math.cos(pitch)
        self.cameraFront = glm.normalize(front)
        
        pitch_x = -pitch * (glm.cos(-math.pi/2+yaw))
        pitch_z = -pitch * (glm.sin(-math.pi/2+yaw))

        self.transform.rotation.xyz = Vec3(pitch_x, math.pi/2-yaw, pitch_z)

    def _physics_update(self, delta_time: float):
        # self._fall_speed += 30 * delta_time**2
        # self.transform.translation.y -= 0.3 * delta_time * self._fall_speed
        # if self.transform.translation.y < self._ground_y:
        #     self.transform.translation.y = self._ground_y
        #     self._fall_speed = 0


    
        input_force = Vec3(*self._rotate_vec_to_face_front(self._keyboardMovementInput))

        if not self.grounded:
            input_force = Vec3(0,0,0)

        if input_force.y > 0:
            input_force.y = 0
            self._momentum.velocity.y = 0.2

        self._momentum.apply_force_walk(input_force, delta_time=delta_time)
        self._momentum.apply_friction(percentage= 0.99 if not self.grounded else 0.84, delta_time=delta_time)
        if not self.grounded:
            self._momentum.apply_force_walk(Vec3(0, -0.3 * self.transform.translation.y, 0), delta_time=delta_time)

        self.transform.translation.xyz += self._momentum.velocity * delta_time * PHYSICS_TPS
        # self.transform.translation.xyz += Vec3(*(cameraStep * delta_time * self.cameraSpeed))


        if self.transform.translation.x > constants.WORLD_SIZE//2:
            self.transform.translation.x = constants.WORLD_SIZE//2
        elif self.transform.translation.x < -constants.WORLD_SIZE//2:
            self.transform.translation.x = -constants.WORLD_SIZE//2
        if self.transform.translation.z > constants.WORLD_SIZE//2:
            self.transform.translation.z = constants.WORLD_SIZE//2
        elif self.transform.translation.z < -constants.WORLD_SIZE//2:
            self.transform.translation.z = -constants.WORLD_SIZE//2

        if self.transform.translation.y < self._ground_y:
            self.transform.translation.y = self._ground_y
        


        return super()._physics_update(delta_time)
