from dataclasses import dataclass
from mimetypes import init
import numpy as np

from OpenGL import GL as gl

from shader import Shader

BASE_SIZE = 1/16 * (1 - (-1))

@dataclass(init=False)
class Ship:
    x: float = 0
    y: float = 0
    z: float = 0
    speed: float = 0
    angle: float = 0
    energy: float = 1 # [1, 2]: indicates glow intensity

    def __init__(self, initial_coords: tuple[float, float, float] = (0,0,0)):
        self._vertices = [ # 2D Triangle
            # X, Y, Z
            -BASE_SIZE, -BASE_SIZE, 0.0,
            +BASE_SIZE, -BASE_SIZE, 0.0,
            0.0, +BASE_SIZE, 0.0,
        ]

        self.x, self.y, self.z = initial_coords

        self.vao = gl.glGenVertexArrays(1)
        self.vbo = gl.glGenBuffers(1)

        gl.glBindVertexArray(self.vao)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.vbo)

        # Set the vertex buffer data
        gl.glBufferData(gl.GL_ARRAY_BUFFER, len(self._vertices)*4, (gl.GLfloat * len(self._vertices))(*self._vertices), gl.GL_DYNAMIC_DRAW)

        self.shader = Shader('shaders/ship/ship.vert', 'shaders/ship/ship.frag')
        self.shader.use()

        gl.glEnableVertexAttribArray(0)
        gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, gl.GL_FALSE, 0, None)

        gl.glEnableVertexAttribArray(1)
        gl.glVertexAttribPointer(1, 1, gl.GL_FLOAT, gl.GL_FALSE, 0, None)

        # gl.glUseProgram(0) # Unbind the shader
        # gl.glBindVertexArray(0) # Unbind the VAO
        # gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0) # Unbind the VBO
        
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

        print(f'Transformation Matrix: \n{transformation_matrix}')

        # Render

        # Bind the shader and VAO (VBO is bound in the VAO)
        gl.glBindVertexArray(self.vao)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.vbo)
        self.shader.use()

        # Set the transformation matrix
        self.shader.set_uniform_matrix('transformation', transformation_matrix)

        # Draw the triangles
        gl.glColor3f(1.0, 0.0, 0.0)
        gl.glDrawArrays(gl.GL_TRIANGLES, 0, len(self._vertices))
        
        pass