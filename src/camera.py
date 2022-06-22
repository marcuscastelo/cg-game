from dataclasses import dataclass
from itertools import accumulate
import math
from shutil import move
import glm
import constants
import glfw

@dataclass
class Camera:
    cameraPos   = glm.vec3(0.0,  0.0,  1.0)
    cameraFront = glm.vec3(0.0,  0.0, -1.0)
    cameraUp    = glm.vec3(0.0,  1.0,  0.0)
    cameraSpeed = 1

    firstMouse = True
    yaw = -75
    pitch = 0.0
    lastX =  constants.WINDOW_SIZE[0]/2
    lastY =  constants.WINDOW_SIZE[1]/2

    _keyboardMovementInput = glm.vec3(0, 0, 0)

    @property
    def cameraRight(self):
        return glm.normalize(glm.cross(self.cameraFront, self.cameraUp))

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

            print(f'{self.cameraSpeed=}')
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

        print(f'Keyboard input: {self._keyboardMovementInput}')


    def _rotate_vec_to_face_front(self, vec: glm.vec3) -> glm.vec3:
        aligned_vec = vec
        aligned_vec = glm.rotateY(aligned_vec, math.radians(-self.yaw))
        return aligned_vec

    def on_mouse(self, window, xpos, ypos):
        if self.firstMouse:
            self.lastX = xpos
            self.lastY = ypos
            self.firstMouse = False

        xoffset = xpos - self.lastX
        yoffset = self.lastY - ypos
        self.lastX = xpos
        self.lastY = ypos

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
