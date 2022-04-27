#version 330

layout(location = 0) out vec4 color;

in vec2 v_TexCoord;

uniform sampler2D u_Texture;

void main() {
    // color = vec4(v_TexCoord, 0.0, 1.0);
    // color = vec4(1.0, 0.0, 0.0, 1.0);
    color = texture(u_Texture, v_TexCoord);
    color = mix(color, vec4(1.0, 0.0, 0.0, 1.0), 0.5);
}