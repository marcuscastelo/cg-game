from dataclasses import dataclass
import math
from shutil import move
import glm
import constants
import glfw

@dataclass
class Camera:
    cameraPos   = glm.vec3(0.0,  0.0,  1.0);
    cameraFront = glm.vec3(0.0,  0.0, -1.0);
    cameraUp    = glm.vec3(0.0,  1.0,  0.0);
    cameraSpeed = 0.01

    firstMouse = True
    yaw = -90.0 
    pitch = 0.0
    lastX =  constants.WINDOW_SIZE[0]/2
    lastY =  constants.WINDOW_SIZE[1]/2

    _movementInput = glm.vec3(0)

    @property
    def cameraRight(self):
        return glm.normalize(glm.cross(self.cameraFront, self.cameraUp))

    def set_movement(self, movement_input: glm.vec3):
        self._movementInput = movement_input
        pass
    
    def update(self, delta: float):
        self.cameraPos += self._movementInput * delta

    def on_key(self, window, key: int, scancode, action: int, mods):
        positive_actions = [ glfw.PRESS ]
        negative_actions = [ glfw.RELEASE ]

        if action not in (positive_actions + negative_actions):
            return

        invert_keymap = action in negative_actions

        keymap = {
            glfw.KEY_W: + self.cameraFront,
            glfw.KEY_S: - self.cameraFront,
            glfw.KEY_D: + self.cameraRight,
            glfw.KEY_A: - self.cameraRight,
            glfw.KEY_SPACE: + self.cameraUp,
            glfw.KEY_LEFT_SHIFT: - self.cameraUp,
        }

        
        self.cameraSpeed = 0.01
        movement = self._movementInput

        for keybind, direction in keymap.items():
            if invert_keymap:
                direction = -direction
            if key == keybind:
                movement += direction
                
        movement = glm.normalize(movement)
        self.set_movement(movement)

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
