#version 330

in vec3 a_Position;
uniform mat4 u_Transformation;

void main() {
    gl_Position = vec4(a_Position, 1.0) * u_Transformation;
}