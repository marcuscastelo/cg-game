#version 330

layout(location = 0) in vec3 a_Position;
layout(location = 1) in vec2 a_TexCoord; 

uniform mat4 u_Transformation;

out vec2 v_TexCoord;

void main() {
    gl_Position = vec4(a_Position, 1.0) * u_Transformation;
    v_TexCoord = a_TexCoord;
}

