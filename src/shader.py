from OpenGL import GL as gl

class Shader:
    def __init__(self, vert_path: str, frag_path: str):
        self.frag_path = frag_path
        self.vert_path = vert_path
        self.program = None
        self._compile()
        self._link()

    def _compile(self):
        with open(self.vert_path, 'r') as f:
            vert_source = f.read()
        with open(self.frag_path, 'r') as f:
            frag_source = f.read()
        self.program = gl.glCreateProgram()
        vert_shader = gl.glCreateShader(gl.GL_VERTEX_SHADER)
        frag_shader = gl.glCreateShader(gl.GL_FRAGMENT_SHADER)
        gl.glShaderSource(vert_shader, vert_source)
        gl.glShaderSource(frag_shader, frag_source)
        gl.glCompileShader(vert_shader)
        gl.glCompileShader(frag_shader)
        gl.glAttachShader(self.program, vert_shader)
        gl.glAttachShader(self.program, frag_shader)

    def _link(self):
        gl.glLinkProgram(self.program)

    
    def use(self):
        gl.glUseProgram(self.program)

    def set_uniform(self, name: str, value):
        if name in self.uniforms:
            gl.glUniform1f(self.uniforms[name], value)
        else:
            print(f'Uniform {name} not found')


    def set_uniform_matrix(self, name: str, value):
        if name in self.uniforms:
            gl.glUniformMatrix4fv(self.uniforms[name], 1, gl.GL_FALSE, value)
        else:
            print(f'Uniform {name} not found')