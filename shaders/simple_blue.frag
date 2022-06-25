#version 330
layout(location = 0) out vec4 o_Color;

in vec3 v_Position;

void main() {
    o_Color = vec4(pow(v_Position.z,3), pow(v_Position.z,3), v_Position.z + 0.5, 1.0);
}