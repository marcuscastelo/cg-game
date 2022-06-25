#version 330

in vec3 a_Position;
uniform mat4 u_Model;
uniform mat4 u_View;
uniform mat4 u_Projection;


void main() {
    gl_Position = vec4(a_Position, 1.0) * u_Model * u_View * u_Projection;
}