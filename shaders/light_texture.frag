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

uniform vec3 u_AuxRobotPos;
uniform vec3 u_BulletPos;
uniform vec3 u_CameraPos;
uniform bool u_HasTexture;

// Constants
vec3 auxRobotLight = vec3(1.0, 1.0, 1.0);
vec3 bulletLight = vec3(1.0, 0.0, 0.0);

void main() {
    // Normalize normals
    vec3 fragNormal = normalize(v_Normal);

    // Calc distance to light source (used to dim)
    float distToAuxBot = length(u_AuxRobotPos - v_Position);
    float distToBullet = length(u_BulletPos - v_Position);

    // Direction to the light (normalized)
    vec3 directionToAuxBot = normalize(u_AuxRobotPos - v_Position);
    vec3 directionToBullet = normalize(u_BulletPos - v_Position);

    // Calc diffuse light
    float auxRobotDiffuseAngularCoeff = max(dot(fragNormal, directionToAuxBot), 0);
    vec3 auxRobotDiffuseLight = max((u_GKd) * u_Kd * auxRobotLight * auxRobotDiffuseAngularCoeff * 1/log2(log2(distToAuxBot+2) + 2), 0);

    float bulletDiffuseAngularCoeff = max(dot(fragNormal, directionToBullet), 0);
    vec3 bulletDiffuseLight = max((u_GKd) * u_Kd * bulletLight * bulletDiffuseAngularCoeff * 1/log2(log2(distToBullet+2) + 2), 0);

    // Calc ambient light
    vec3 ambientLight = max((u_GKa) * (u_Kd) * auxRobotLight, 0);
    float directionalCoeff = dot(vec3(0,0,1), fragNormal) / 3;
    vec3 ambientDirectionalLight = max((u_GKa) * (u_Ka) * directionalCoeff * auxRobotLight, 0);

    // Calc specular light
    vec3 cameraDiretion = normalize(u_CameraPos - v_Position);
    vec3 reflectDirection = normalize(reflect(-directionToAuxBot, fragNormal));
    float dotProduct = max(dot(cameraDiretion, reflectDirection), 0.0);
    float specMultiplier = pow(dotProduct, (u_GNs) * u_Ns); //TODO: check if this multiplication makes sense (u_Ns * (u_GKs))
    vec3 specularLight = max((u_GKs) * u_Ks * specMultiplier * auxRobotLight * 1/log2(distToAuxBot+1), 0);

    vec4 fragBaseColor;
    if (u_HasTexture)
        fragBaseColor = texture2D(u_Texture, v_TexCoord);
    else
        fragBaseColor = vec4(u_Kd, 1.0);

    vec3 combinedLight = ambientLight + ambientDirectionalLight + auxRobotDiffuseLight + bulletDiffuseLight + specularLight;

    color = vec4((combinedLight) * fragBaseColor.xyz, u_d);
    // color = vec4(fragBaseColor.xyz, u_d);
}