from OpenGL import GL as gl
import numpy as np
from utils.logger import LOGGER

class Shader:
    def __init__(self, vert_path: str, frag_path: str):
        self.frag_path = frag_path
        self.vert_path = vert_path

        self.vert_shader = None
        self.frag_shader = None
        self.program = gl.glCreateProgram()
        self._compile()
        self._link()

    def _load_source(self, path: str) -> str:
        with open(path, 'r') as f:
            return f.read()
    
    def _compile(self):
        # Load shaders source code from files
        vert_source = self._load_source(self.vert_path)
        frag_source = self._load_source(self.frag_path)

        # Create shaders
        self.vert_shader = int(gl.glCreateShader(gl.GL_VERTEX_SHADER))
        self.frag_shader = int(gl.glCreateShader(gl.GL_FRAGMENT_SHADER))

        # Set source        
        gl.glShaderSource(self.vert_shader, vert_source)
        gl.glShaderSource(self.frag_shader, frag_source)
        
        # Compile shaders
        gl.glCompileShader(self.vert_shader)
        gl.glCompileShader(self.frag_shader)

        def _cleanup_compile_error():
            gl.glDeleteShader(self.vert_shader)
            gl.glDeleteShader(self.frag_shader)
            gl.glDeleteProgram(self.program)
            self.program = self.vert_shader = self.frag_shader = None

        # Check for errors
        if self.vert_shader is None or self.frag_shader is None:
            _cleanup_compile_error()
            LOGGER.log_error(f'Error compiling {self.vert_path} and {self.frag_path}: one of the shaders was None')
            raise RuntimeError(f'Error compiling {self.vert_path} and {self.frag_path}')
        else:
            LOGGER.log_debug(f'Compiled {self.vert_path} and {self.frag_path}')
            LOGGER.log_debug(f'{self.vert_shader=}, {self.frag_shader=}')

        if gl.glGetShaderiv(self.vert_shader, gl.GL_COMPILE_STATUS) != gl.GL_TRUE:
            log = gl.glGetShaderInfoLog(self.vert_shader)
            _cleanup_compile_error()
            raise RuntimeError(f'Error compiling {self.vert_path}: {log}')
        if gl.glGetShaderiv(self.frag_shader, gl.GL_COMPILE_STATUS) != gl.GL_TRUE:
            log = gl.glGetShaderInfoLog(self.frag_shader)
            _cleanup_compile_error()
            raise RuntimeError(f'Error compiling {self.frag_path}: {log}')
        
    def _link(self):
        # Link
        gl.glAttachShader(self.program, self.vert_shader)
        gl.glAttachShader(self.program, self.frag_shader)
        gl.glLinkProgram(self.program)

        # Check for errors
        if gl.glGetProgramiv(self.program, gl.GL_LINK_STATUS) != gl.GL_TRUE:
            self._cleanup()
            raise RuntimeError(f'Error linking {self.vert_path} and {self.frag_path}: {gl.glGetProgramInfoLog(self.program)}')
        

    def _cleanup(self):
        if self.program is None:
            return
        
        if self.vert_shader is not None:
            gl.glDetachShader(self.program, self.vert_shader)
            gl.glDeleteShader(self.vert_shader)
            self.vert_shader = None

        if self.frag_shader is not None:
            gl.glDetachShader(self.program, self.frag_shader)
            gl.glDeleteShader(self.frag_shader)
            self.frag_shader = None

        gl.glDeleteProgram(self.program)
        self.program = None
    
    def __del__(self):
        self._cleanup()

    def use(self):
        gl.glUseProgram(self.program)

    def set_uniform_matrix(self, name: str, value: np.ndarray):
        uniform_loc = gl.glGetUniformLocation(self.program, name)
        gl.glUniformMatrix4fv(uniform_loc, 1, gl.GL_FALSE, value)

