from OpenGL import GL as gl
import numpy as np
from utils.geometry import Vec3
from utils.logger import LOGGER

from gl_abstractions.layout import Layout

import glfw

class Shader:
    def __init__(self, vert_path: str, frag_path: str, layout: Layout):
        assert glfw.get_current_context(), f'Trying to create a shader with no OpenGL Context'


        self.frag_path = frag_path
        self.vert_path = vert_path
        self.layout = layout

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
            log = gl.glGetProgramInfoLog(self.program)
            self._cleanup()
            raise RuntimeError(f'Error linking {self.vert_path} and {self.frag_path}: {log}')

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

    def upload_uniform_matrix4f(self, name: str, value: np.ndarray):
        uniform_loc = gl.glGetUniformLocation(self.program, name)
        gl.glUniformMatrix4fv(uniform_loc, 1, gl.GL_FALSE, value)

    def upload_uniform_int(self, name: str, value: int):
        uniform_loc = gl.glGetUniformLocation(self.program, name)
        gl.glUniform1i(uniform_loc, value)

    def upload_uniform_float(self, name: str, value: float):
        uniform_loc = gl.glGetUniformLocation(self.program, name)
        gl.glUniform1f(uniform_loc, value)

    def upload_uniform_vec3(self, name: str, value: np.ndarray):
        uniform_loc = gl.glGetUniformLocation(self.program, name)
        gl.glUniform3f(uniform_loc, *value)

    def upload_bool(self, name: str, value: bool):
        uniform_loc = gl.glGetUniformLocation(self.program, name)
        gl.glUniform1i(uniform_loc, value)

        pass

    def __repr__(self) -> str:
        return f'<Shader v={self.vert_path} f={self.frag_path}>'
    

class ShaderDB:
    _instance: 'ShaderDB' = None
    def __init__(self):
        self.shaders: dict[str, Shader] = {}

        self.shaders['light_texture'] = Shader(
            'shaders/light_texture.vert','shaders/light_texture.frag',
            layout=Layout([
                ('a_Position', 3),
                ('a_TexCoord', 2),
                ('a_Normal', 3)
            ])
        )

    def get_shader(self, name: str):
        return self.shaders[name]

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __getitem__(self, key):
        return self.shaders[key]

    def __setitem__(self, key, value):
        self.shaders[key] = value

    def __delitem__(self, key):
        del self.shaders[key]
    
    def __contains__(self, key):
        return key in self.shaders

    def __iter__(self):
        return iter(self.shaders)

    def __len__(self):
        return len(self.shaders)

    def __str__(self):
        return str(self.shaders)

    def __repr__(self):
        return repr(self.shaders)