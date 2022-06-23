//Textured.vert
#version 330
layout(location = 0) in vec3 a_Position;
layout(location = 1) in vec2 a_TexCoord; 

uniform mat4 u_Model;
uniform mat4 u_View;
uniform mat4 u_Projection;

out vec2 v_TexCoord;

void main() {
    gl_Position = vec4(a_Position, 1.0) * u_Model * u_View * u_Projection;
    v_TexCoord = a_TexCoord;
}

