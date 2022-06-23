from dataclasses import dataclass
from itertools import accumulate
import math
from turtle import shape
import glm
from utils.geometry import Vec3
from utils.sig import metsig
import constants
import glfw

from objects.element import Element, ElementSpecification, ShapeSpec
from objects.world import World
from transform import Transform

class Camera(Element):
    @metsig(Element.__init__)
    def __init__(self, world: World):
        self.cameraPos   = glm.vec3(0.0,  0.0,  1.0)
        self.cameraFront = glm.vec3(0.0,  0.0, -1.0)
        self.cameraUp    = glm.vec3(0.0,  1.0,  0.0)
        self.cameraSpeed = 1

        self.yaw = -75
        self.pitch = 0.0

        self._keyboardMovementInput = glm.vec3(0, 0, 0)
        
        specification = ElementSpecification(
            shape_specs=[] # Camera has no Shape
        )

        super().__init__(world=world, specs=specification)

        print(f'Camera._transform: {self._transform}')

    @property
    def cameraRight(self):
        return glm.normalize(glm.cross(self.cameraFront, self.cameraUp))

    def reset(self):
        new_camera = Camera(self.world)
        for attr in self.__dict__.keys():
            setattr(self, attr, getattr(new_camera, attr))

    def set_movement(self, movement_input: glm.vec3):
        self._keyboardMovementInput = movement_input
        pass
    
    def update(self, delta: float):
        cameraStep = self._rotate_vec_to_face_front(self._keyboardMovementInput)
        self.cameraPos += cameraStep * delta * self.cameraSpeed

    def on_key(self, window, key: int, scancode, action: int, mods):
        positive_actions = [ glfw.PRESS ]
        negative_actions = [ glfw.RELEASE ]

        if key == glfw.KEY_LEFT_CONTROL:
            if action in positive_actions:
                self.cameraSpeed *= 2
            else:
                self.cameraSpeed /= 2

            return

        if action not in (positive_actions + negative_actions):
            return

        direction_vecs = {
            'front':    glm.vec3(+1, 0, 0),
            'back':     glm.vec3(-1, 0, 0),
            'right':    glm.vec3(0, 0, +1),
            'left':     glm.vec3(0, 0, -1),
            'up':       glm.vec3(0, +1, 0),
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

        front = glm.vec3()
        front.x = math.cos(glm.radians(self.yaw)) * math.cos(glm.radians(self.pitch))
        front.y = math.sin(glm.radians(self.pitch))
        front.z = math.sin(glm.radians(self.yaw)) * math.cos(glm.radians(self.pitch))
        self.cameraFront = glm.normalize(front)