#ifndef CAMERA_HPP
#define CAMERA_HPP

#include <GL/glew.h>
#include <GL/gl.h>  /* verifique no seu SO onde fica o gl.h */
#define GLFW_INCLUDE_NONE
#include <GLFW/glfw3.h> /* verifique no seu SO onde fica o glfw3.h */
#include <math.h>
#include <glm/matrix.hpp>
#include <glm/gtx/transform.hpp>
#include <glm/gtc/type_ptr.hpp>
#include <glm/gtx/string_cast.hpp>

//Classe da camera utilizada no cenario
class camera{
private:
    glm::vec3 pos;      //Posicao da camera
    glm::vec3 front;    //Ponto para onde a camera esta olhando
    glm::vec3 up;       //Vetor viewUP
    float fov;          //angulo de fov da projection
    float aspect_ratio; //aspect-ratio da janela
    float near;         //Planos de corte em z-view
    float far;
    GLuint program;     //ID do Programa na GPU
    bool freeCamera;    //Ativa o modo free camera, andar pelo cenario livremente
    float speed;        //Velocidade na qual a camera anda pelo cenario
    float sensibility;
public:
    camera(GLuint program, glm::vec3 pos, glm::vec3 front, glm::vec3 up, 
    float fov, float aspect_ratio, float near, float far, bool freeCamera);
    
    //Movimentacao da camera pelo cenario
    void moveFront(float deltaTime);
    void moveBack(float deltaTime);
    void moveLeft(float deltaTime);
    void moveRight(float deltaTime);

    //Calcula as matrizes de view e projection e manda para a gpu
    void update();

    //Metodos Set
    void setPos(glm::vec3 pos);
    void setFront(glm::vec3 front);
    void setUp(glm::vec3 up);
    void setFov(float fov);
    void setAspectRatio(float aspect_ratio);
    void setNear(float near);
    void setFar(float far);
    void setCameraMode(bool freeCamera);
    void setSpeed(float speed);
    void setSensibility(float sensibility);

    glm::vec3 getPos();
    ~camera();
};

#endif