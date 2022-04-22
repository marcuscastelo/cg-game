#version 330
in vec3 o_color;
void main() {
    gl_FragColor = vec4(o_color, 1.0);
}