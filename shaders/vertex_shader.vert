#version 330
in vec2 position;
uniform mat4 mvp;
void main() {
    gl_Position = vec4(position, 0.0, 1.0) * mvp;
}