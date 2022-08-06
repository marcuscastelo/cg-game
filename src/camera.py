from dataclasses import dataclass, field
import math
import glm
from utils.geometry import Vec2, Vec3
import constants
import glfw
from line import Line
from objects.bullet_ray import BulletRay

from objects.element import PHYSICS_TPS, Element, ShapeSpec
from objects.model_element import ModelElement
from objects.physics.momentum import Momentum
from objects.physics.rotation import front_to_rotation, yaw_pitch_to_front
from objects.selection_ray import SelectionRay
from objects.world import World
from objects.selection_ray import SelectionRay

from input.input_system import INPUT_SYSTEM as IS
from wavefront.model_reader import ModelReader


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
        # self.ray: Line = None
        self.gun: ModelElement = None

    def on_spawned(self, world: 'World'):
        # TODO: fix shader
        self.raycast_line_dbg = Line('test_line', ray_selectable=False, ray_destroyable=False)
        self.raycast_line_dbg.shape_specs[0].material.Ka.z = 10
        self.raycast_line_dbg.transform.scale.z = 10
        # world.spawn(self.raycast_line_dbg)

        self.gun = ModelElement('PlayerGun', model=ModelReader().load_model_from_file('models/gun.obj'), ray_selectable=False, ray_destroyable=False)
        self.gun.transform.scale *= 0.1
        world.spawn(self.gun)
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

    def _update_from_pitch_yaw(self):
        if self.pitch >= 89.9: self.pitch = 89.9
        if self.pitch <= -89.9: self.pitch = -89.9

        yaw = glm.radians(self.yaw)
        pitch = glm.radians(self.pitch)

        self.cameraFront = glm.vec3(*yaw_pitch_to_front(yaw, pitch))

        self.transform.rotation.xyz = front_to_rotation(Vec3(*self.cameraFront))

    def update(self, delta_time: float):
        yaw = glm.radians(self.yaw)
        pitch = glm.radians(self.pitch)
        self.cameraFront = glm.vec3(*yaw_pitch_to_front(yaw, pitch))
        self.transform.rotation.xyz = front_to_rotation(Vec3(*self.cameraFront))

        super().update(delta_time)
        pass

    def on_key(self, window, key: int, scancode, action: int, mods):
        # TODO: remove debug
        from app_vars import APP_VARS
        if IS.just_pressed('e'):
            world = APP_VARS.world
            selection_ray = SelectionRay('PlayerSelectionRay', show_debug_cube=False)
            selection_ray.cast(
                world=world,
                origin=self.transform.translation.xyz - Vec3(0,0.1,0) + Vec3(*self.cameraFront) * 1,
                direction=Vec3(*self.cameraFront).normalized()
            )
        elif IS.just_pressed('r'):
            world = APP_VARS.world
            bullet_ray = BulletRay('PlayerBulletRay', show_debug_cube=True)
            bullet_ray.cast(
                world=world,
                origin=self.transform.translation.xyz - Vec3(0,0.1,0) + Vec3(*self.cameraFront) * 1,
                direction=Vec3(*self.cameraFront).normalized()
            )

            self.gun.transform.translation -= Vec3(*self.cameraFront) * 0.1
            self.gun.transform.translation -= Vec3(*self.cameraUp) * 0.05
            self.pitch += 3
            self._update_from_pitch_yaw()

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

    def _rotate_vec_to_face_front(self, vec: glm.vec3) -> glm.vec3:
        aligned_vec = vec
        aligned_vec = glm.rotateY(aligned_vec, math.radians(-self.yaw))
        return aligned_vec

    def on_cursor_pos(self, window, xpos, ypos):
        # TODO: change on physiscs tick to make gun move smoothly
        from app_vars import APP_VARS
        from objects.physics.rotation import front_to_yaw_pitch

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

        self._update_from_pitch_yaw

    def _physics_update(self, delta_time: float):
        self.raycast_line_dbg.transform.translation.xz = self.transform.translation.xz
        self.raycast_line_dbg.transform.translation.y = self._ground_y - 0.05
        self.raycast_line_dbg.transform.rotation.xyz = self.transform.rotation.xyz

        # TODO: make all gun logic in one place plz
        self.gun.transform.rotation.y = self.transform.rotation.y - math.pi/2
        self.gun.transform.rotation.xz = self.transform.rotation.xz
        
      

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

        input_force = Vec3(*self._rotate_vec_to_face_front(self._keyboardMovementInput))

        if not self.grounded:
            input_force = Vec3(0,0,0)

        if input_force.y > 0:
            input_force.y = 0
            self._momentum.velocity.y = 0.2

        self._momentum.apply_force_walk(input_force, delta_time=delta_time)
        self._momentum.apply_friction(percentage_keep= 0.99 if not self.grounded else 0.84, delta_time=delta_time)
        if not self.grounded:
            self._momentum.apply_force_walk(Vec3(0, -0.3 * self.transform.translation.y, 0), delta_time=delta_time)

        self.transform.translation.xyz += self._momentum.velocity * delta_time * PHYSICS_TPS

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
        
        # TODO: make all gun logic in one place plz
        self.gun.transform.translation.xz = self.transform.translation.xz + Vec2(1,-1) * (math.sin(self.transform.translation.x) + math.cos(self.transform.translation.z))/150 + Vec2(-1,1) * (math.cos(self.transform.translation.x) + math.sin(self.transform.translation.z))/150
        self.gun.transform.translation.y = self.transform.translation.y - 0.25 + (math.sin(self.transform.translation.x) + math.sin(self.transform.translation.z))/40
        self.gun.transform.translation.xyz += (Vec3(*self.cameraFront)) / 3
        
        if IS.is_pressed('f'):
            self.gun.transform.rotation.y = self.transform.rotation.y

        return super()._physics_update(delta_time)
