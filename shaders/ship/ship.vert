#version 330

/*layout (location = 0)*/
in vec3 vPosition;
/*layout (location = 1)*/
uniform mat4 transformation;

// layout (location = 2) in vec2 texCoordIn;

// out vec2 texCoordOut;
// 

void main() {
    gl_Position = vec4(vPosition, 1.0) * transformation;
    // texCoordOut = texCoordIn; // TODO: make this without passing through (see https://www.khronos.org/opengl/wiki/Vertex_Post-Processing)
}