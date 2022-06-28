#version 330
layout(location = 0) out vec4 color;

// Passed by vertex shader
in vec3 v_Position;
in vec2 v_TexCoord;
in vec3 v_Normal;

// Uniforms
uniform sampler2D u_Texture;

uniform vec3 u_Ka; // Ambient Coeff.
uniform vec3 u_Kd; // Diffuse Coeff.
uniform vec3 u_Ks; // Specular Coeff.
uniform float u_Ns; // Specular Exponent.

uniform vec3 u_GKa; // Ambient Coeff.
uniform vec3 u_GKd; // Diffuse Coeff.
uniform vec3 u_GKs; // Specular Coeff.
uniform float u_GNs; // Specular Exponent.

uniform float u_d;

uniform vec3 u_LightPos;
uniform vec3 u_CameraPos;

// Constants
vec3 lightColor = vec3(1.0, 1.0, 1.0);

void main() {
    // Normalize normals
    vec3 fragNormal = normalize(v_Normal);

    // Calc distance to light source (used to dim)
    float distToLight = length(u_LightPos - v_Position);

    // Direction to the light (normalized)
    vec3 lightDirection = normalize(u_LightPos - v_Position);

    // Calc diffuse light
    float diffuseAngularCoeff = max(dot(fragNormal, lightDirection), 0);
    vec3 diffuseLight = max((u_GKd) * u_Kd * lightColor * diffuseAngularCoeff * 1/log2(distToLight+1), 0);

    // Calc ambient light
    vec3 ambientLight = max((u_GKa) * (u_Kd) * lightColor, 0);
    float directionalCoeff = max(dot(vec3(0,0,1), fragNormal), 0) / 3;
    vec3 ambientDirectionalLight = max((u_GKa) * (u_Ka) * directionalCoeff * lightColor, 0);

    // Calc specular light
    vec3 cameraDiretion = normalize(u_CameraPos - v_Position);
    vec3 reflectDirection = normalize(reflect(-lightDirection, fragNormal));
    float dotProduct = max(dot(cameraDiretion, reflectDirection), 0.0);
    float specMultiplier = pow(dotProduct, (u_GNs) * u_Ns); //TODO: check if this multiplication makes sense (u_Ns * (u_GKs))
    vec3 specularLight = max((u_GKs) * u_Ks * specMultiplier * lightColor * 1/log2(distToLight+1), 0);

    vec4 fragTextureColor = texture2D(u_Texture, v_TexCoord);
    vec3 combinedLight = ambientLight + ambientDirectionalLight + diffuseLight + specularLight;

    color = vec4(combinedLight * fragTextureColor.xyz, u_d);
}