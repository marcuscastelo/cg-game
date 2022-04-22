#version 330
in vec3 position;
uniform mat4 mvp;

out vec3 o_color;
void main() {
    gl_Position = vec4(position, 1.0) * mvp;
    

    o_color = position/2+0.5;
}