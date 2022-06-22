#include "camera.hpp"

//Construtor da camera
camera::camera(GLuint program, glm::vec3 pos, glm::vec3 front, glm::vec3 up, float fov, float aspect_ratio, float near, float far, bool freeCamera = true){
    this->program = program;
    this->pos = pos;
    this->front = front;
    this->up = up;
    this->fov = fov;
    this->aspect_ratio = aspect_ratio;
    this->near = near;
    this->far = far;
    this->freeCamera = freeCamera;
    this->speed = 3.5f;
    this->sensibility = 2.5f;
}

//Movimentacao da camera para frente
void camera::moveFront(float deltaTime){
    if(this->freeCamera){
        this->pos += this->speed * this->front * deltaTime;
    }
    else{ //Nao eh uma free camera, logo y constante
        this->pos.x += this->speed * this->front.x * deltaTime;
        this->pos.z += this->speed * this->front.z * deltaTime;
    }
}

//Movimentacao da camera para tras
void camera::moveBack(float deltaTime){
    if(this->freeCamera){
        this->pos -= this->speed * this->front * deltaTime;
    }
    else{ //Nao eh uma free camera, logo y constante
        this->pos.x -= this->speed * this->front.x * deltaTime;
        this->pos.z -= this->speed * this->front.z * deltaTime;
    }
}

//Movimentacao da camera para esquerda
void camera::moveLeft(float deltaTime){
    if(this->freeCamera){
        this->pos -= glm::normalize(glm::cross(this->front, this->up)) * this->speed * deltaTime; 
    }
    else{
        this->pos.x -= glm::normalize(glm::cross(this->front, this->up).x) * this->speed * deltaTime;
        this->pos.z -= glm::normalize(glm::cross(this->front, this->up).z) * this->speed * deltaTime;
    }
}

//Movimentacao da camera para direita
void camera::moveRight(float deltaTime){
    if(this->freeCamera){
        this->pos += glm::normalize(glm::cross(this->front, this->up)) * this->speed * deltaTime; 
    }
    else{
        this->pos.x += glm::normalize(glm::cross(this->front, this->up).x) * this->speed * deltaTime;
        this->pos.z += glm::normalize(glm::cross(this->front, this->up).z) * this->speed * deltaTime;
    }
}

//Calcula os valores das matrizes de view e projection e manda para a gpu
void camera::update(){
    if(this->pos.x > 14.0f){ //Limites em x da camera no cenario
        this->pos.x = 14.0f;
    }
    else if(this->pos.x < -14.0f){
        this->pos.x = -14.0f;
    }

    if(this->pos.y > 14.0f){ //Limites em y da camera no cenario
        this->pos.y = 14.0f;
    }
    else if(this->pos.y < 0.1f){
        this->pos.y = 0.1f;
    }


    if(this->pos.z > 14.0f){  //Limites em z da camera no cenario
        this->pos.z = 14.0f;
    }
    else if(this->pos.z < -14.0f){
        this->pos.z = -14.0f;
    }
    
    
    //Calculo das matrizes de view e projection
    glm::mat4 m_view = glm::lookAt(this->pos, this->pos + this->front, this->up);
    glm::mat4 m_projection = glm::perspective(glm::radians(this->fov), this->aspect_ratio, this->near, this->far);

    //Manda para a gpu a matriz de view
    int loc_view = glGetUniformLocation(program, "view");
    glUniformMatrix4fv(loc_view, 1, GL_FALSE, glm::value_ptr(m_view));

    //Manda para a gpu a matriz de projection
    int loc_projection = glGetUniformLocation(program, "projection");
    glUniformMatrix4fv(loc_projection, 1, GL_FALSE,glm::value_ptr(m_projection));    
}


//Sets methods
void camera::setPos(glm::vec3 pos){
    this->pos = pos;
}

void camera::setFront(glm::vec3 front){
    this->front = front;
}

void camera::setUp(glm::vec3 up){
    this->up = up;
}

void camera::setFov(float fov){
    this->fov = fov;
}

void camera::setAspectRatio(float aspect_ratio){
    this->aspect_ratio = aspect_ratio;
}

void camera::setNear(float near){
    this->near = near;
}

void camera::setFar(float far){
    this->far = far;
}

void camera::setCameraMode(bool freeCamera){
    this->freeCamera = freeCamera;
}

void camera::setSpeed(float speed){
    this->speed = speed;
}

void camera::setSensibility(float sensibility){
    this->sensibility = sensibility;
}

glm::vec3 camera::getPos(){
    return this->pos;
}

camera::~camera(){}