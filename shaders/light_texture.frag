#version 330
layout(location = 0) out vec4 color;

// Passed by vertex shader
in vec3 v_Position;
in vec2 v_TexCoord;
in vec3 v_Normal;

// Uniforms
uniform sampler2D u_Texture;

uniform float u_Ka;
uniform float u_Kd;
uniform vec3 u_LightPos;

// Constants
vec3 lightColor = vec3(1.0, 1.0, 1.0);

void main() {
    vec3 normal = normalize(v_Normal);
    float distToLight = length(u_LightPos - v_Position);

    // Direction to the light (normalized)
    vec3 lightDirection = normalize(u_LightPos - v_Position);
    float diffuseAngularCoeff = max(dot(normal, lightDirection), 0.1);

    
    vec3 ambientLight = u_Ka * lightColor;
    vec3 diffuseLight = u_Kd * lightColor * diffuseAngularCoeff * 1/sqrt((distToLight * diffuseAngularCoeff));


    vec4 fragTextureColor = texture2D(u_Texture, v_TexCoord);
    vec3 combinedLight = ambientLight + diffuseLight;

    color = vec4(combinedLight * fragTextureColor.xyz, 1.0);
}