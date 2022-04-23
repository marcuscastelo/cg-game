from dataclasses import dataclass
import numpy as np

from OpenGL import GL as gl

BASE_SIZE = 1/4 * (1 - (-1))

@dataclass
class Ship:
    x: float = 0
    y: float = 0
    z: float = 0
    speed: float = 0
    angle: float = 0
    energy: float = 0 # [0, 1]: indicates glow intensity

    def __init__(self):
        self._vertices = [ # 2D Triangle
            # X, Y, Z
            -BASE_SIZE, -BASE_SIZE, 0,
            +BASE_SIZE, -BASE_SIZE, 0,
            0, +BASE_SIZE, 0,
        ]

        self._shader_program = gl.glCreateProgram()
        
    def render(self):
        # Calculate Transformation Matrix
        transformation_matrix = np.eye(4, dtype=np.float32)

        # Scale Matrix
        scale_matrix = np.eye(4, dtype=np.float32)
        scale_matrix[0][0] = self.energy
        scale_matrix[1][1] = self.energy
        scale_matrix[2][2] = self.energy
        scale_matrix[3][3] = self.energy

        # Rotation Matrix
        rotation_matrix = np.eye(4, dtype=np.float32)
        rotation_matrix[0][0] = np.cos(self.angle)
        rotation_matrix[0][1] = -np.sin(self.angle)
        rotation_matrix[1][0] = np.sin(self.angle)
        rotation_matrix[1][1] = np.cos(self.angle)

        # Translation Matrix
        translation_matrix = np.eye(4, dtype=np.float32)
        translation_matrix[0][3] = self.x
        translation_matrix[1][3] = self.y
        translation_matrix[2][3] = self.z

        # Calculate Transformation Matrix
        transformation_matrix = np.matmul(translation_matrix, rotation_matrix)
        transformation_matrix = np.matmul(transformation_matrix, scale_matrix)

        # Render
        gl.glUseProgram(0)


        pass