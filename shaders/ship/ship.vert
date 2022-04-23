#version 330
in vec3 position;
uniform mat4 transformation;

void main() {
    gl_Position = vec4(position, 1.0) * transformation;
}