#version 330

layout(location=0) in vec3 a_Position;
layout(location=1) in vec2 a_TexCoord;
layout(location=2) in vec3 a_Normal;

// MVP
uniform mat4 u_Model;
uniform mat4 u_View;
uniform mat4 u_Projection;

out vec3 v_Position;
out vec2 v_TexCoord;
out vec3 v_Normal;

void main() {
    gl_Position = vec4(a_Position, 1.0) * u_Model * u_View * u_Projection;
    v_Position = (vec4(a_Position, 1.0) * u_Model).xyz;
    v_TexCoord = a_TexCoord;
    v_Normal = (vec4(a_Normal, 0.0) * u_Model).xyz;
}