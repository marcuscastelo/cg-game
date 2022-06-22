#include <GL/glew.h>
#include <GL/gl.h>  
#define GLFW_INCLUDE_NONE
#include <GLFW/glfw3.h> 
#include <iostream>
#include <stdlib.h>
#include <stdio.h>
#include <math.h>
#include <glm/matrix.hpp>
#include <glm/gtx/transform.hpp>
#include <glm/gtc/type_ptr.hpp>
#include <glm/gtx/string_cast.hpp>

#include "camera.hpp"
#include "mesh.hpp"

int altura = 1000;
int largura = 1000;

float deltaTime = 0.0f;	//Tempo entre o ultimo frame e o atual. Usado para obter uma movimentacao mais "suave" da camera pelo cenario
float lastFrame = 0.0f; //Tempo do ultimo frame 

glm::vec3 cameraFront(0.0,  -5.0, -10.0); //Variavel global para matriz View


//Variaveis globais de controle de tecla
bool stop = false;          //Caso a tecla para fechar o programa seja apertada
bool polygonMode = false;   //Caso a tecla para modo poligono seja apertada
bool W = false;             //Caso a tecla W seja apertada
bool A = false;             //Caso a tecla A seja apertada
bool S = false;             //Caso a tecla S seja apertada
bool D = false;             //Caso a tecla D seja apertada


//Funcao de callback para eventos de teclado
static void key_callback(GLFWwindow* window, int key, int scancode, int action, int mods){
    float cameraSpeed = 0.1;
    if(key == 87 && (action==1 || action==2)){ //Se tecla W apertada
        W = true;
    }
    if(key == 83 && (action==1 || action==2)){ //Se tecla S apertada
        S = true;
    }
    if(key == 65 && (action==1 || action==2)){ //Se tecla A apertada
        A = true;    
    }
    if(key == 68 && (action==1 || action==2)){ //Se tecla D apertada
        D = true;
    }
    if(key == GLFW_KEY_Q && (action==1 || action==2)) //Se tecla Q apertada, entao diz que o programa deve ser fechado
        stop = true;
    if(key == GLFW_KEY_P && (action==1 || action==2)){ //Se tecla P apertada, entao ativara/desativara o modo poligono
        polygonMode = !polygonMode;
    }
}


//Variaveis globais para controle do uso do mouse
float yaw =  -90.0;         
float pitch = 0.0;
float lastX = largura/2;
float lastY = altura/2;

//Funcao que realiza a leitura dos valores do mouse e obtem para onde a camera deve ser apontada
void cursor_position_update(GLFWwindow* window){
    double xpos, ypos;
    glfwGetCursorPos(window,&xpos,&ypos);       //Pega a posicao atual do cursor na tela
    glfwSetCursorPos(window, 500.0, 500.0);     //Muda a posicao do cursor para o centro da tela para a proxima chamada da funcao
    
    float xoffset = xpos - 500;     //Calcula quanto o mouse foi mexido em X desde a ultima chamada da funcao
    float yoffset = 500 - ypos;     //Calcula quanto o mouse foi mexido em Y desde a ultima chamada da funcao, invertido

    float sensitivity = 2.5f;              //Sensibilidade da camera
    xoffset *= sensitivity * deltaTime;    //Calcula o quanto o angulo da camera em X foi alterado 
    yoffset *= sensitivity * deltaTime;    //Calcula o quanto o angulo da camera em Y foi alterado

    yaw += xoffset;     //Calcula o angulo atual da camera em X
    pitch += yoffset;   //Calcula o angulo atual da camera em Y

    
    if (pitch >= 89.9) pitch = 89.9;    //Define limites para o angulo da camera em Y
    if (pitch <= -89.9) pitch = -89.9;

    //Com base nos angulos da camera em X e Y calcula o ponto para o qual a camera esta olhando
    glm::vec3 front;
    front.x = cos(glm::radians(yaw)) * cos(glm::radians(pitch));
    front.y = sin(glm::radians(pitch));
    front.z = sin(glm::radians(yaw)) * cos(glm::radians(pitch));
    cameraFront = glm::normalize(front);
}

 
int main(void){
 
    // inicicializando o sistema de janelas
    glfwInit();

    // deixando a janela invisivel, por enquanto
    glfwWindowHint(GLFW_VISIBLE, false);

 
    // criando uma janela
    GLFWwindow* window = glfwCreateWindow(largura, altura, "Cenario", NULL, NULL);

    
    // tornando a janela como principal 
    glfwMakeContextCurrent(window);

    // inicializando Glew (para lidar com funcoes OpenGL)
    GLint GlewInitResult = glewInit();
    printf("GlewStatus: %s", glewGetErrorString(GlewInitResult));

    glfwSetKeyCallback(window, key_callback);
    glfwSetInputMode(window, GLFW_CURSOR, GLFW_CURSOR_DISABLED);    //Ativa o modo sem cursor do mouse
    

    // GLSL para Vertex Shader
    char* vertex_code =
    "attribute vec2 texture_coord;\n"
    "varying vec2 out_texture;\n"
    "attribute vec3 position;\n"
    "uniform mat4 model;\n"
    "uniform mat4 view;\n"
    "uniform mat4 projection;\n"
    "void main()\n"
    "{\n"
    "    gl_Position = projection * view * model * vec4(position,1.0);\n"
    "    out_texture = vec2(texture_coord);\n"
    "}\n";

    // GLSL para Fragment Shader
    char* fragment_code =
    "varying vec2 out_texture;\n"
    "uniform sampler2D samplerTexture;\n"
    "uniform vec4 color;\n"
    "void main()\n"
    "{\n"
    "   vec4 texture = texture2D(samplerTexture, out_texture);\n"
    "   gl_FragColor = texture;\n"
    "}\n";

    // Requisitando slot para a GPU para nossos programas Vertex e Fragment Shaders
    GLuint program = glCreateProgram();
    GLuint vertex = glCreateShader(GL_VERTEX_SHADER);
    GLuint fragment = glCreateShader(GL_FRAGMENT_SHADER);

    // Associando nosso código-fonte GLSL aos slots solicitados
    glShaderSource(vertex, 1, &vertex_code, NULL);
    glShaderSource(fragment, 1, &fragment_code, NULL);

    // Compilando o Vertex Shader e verificando erros
    glCompileShader(vertex);

    GLint isCompiled = 0;
    glGetShaderiv(vertex, GL_COMPILE_STATUS, &isCompiled);
    if(isCompiled == GL_FALSE){

        //descobrindo o tamanho do log de erro
        int infoLength = 512;
        glGetShaderiv(vertex, GL_INFO_LOG_LENGTH, &infoLength);

        //recuperando o log de erro e imprimindo na tela
        char info[infoLength];
        glGetShaderInfoLog(vertex, infoLength, NULL, info);

        printf("Erro de compilacao no Vertex Shader.\n");
        printf("--> %s\n",&info);

    }

    

    // Compilando o Fragment Shader e verificando erros
    glCompileShader(fragment);

    isCompiled = 0;
    glGetShaderiv(fragment, GL_COMPILE_STATUS, &isCompiled);
    if(isCompiled == GL_FALSE){

        //descobrindo o tamanho do log de erro
        int infoLength = 512;
        glGetShaderiv(fragment, GL_INFO_LOG_LENGTH, &infoLength);

        //recuperando o log de erro e imprimindo na tela
        char info[infoLength];
        glGetShaderInfoLog(fragment, infoLength, NULL, info);

        printf("Erro de compilacao no Fragment Shader.\n");
        printf("--> %s\n",&info);

    }

    // Associando os programas compilado ao programa principal
    glAttachShader(program, vertex);
    glAttachShader(program, fragment);

    // Linkagem do programa e definindo como default
    glLinkProgram(program);
    glUseProgram(program);
 
    //Diz ao openGL para usar texturas com transparencia
    glHint(GL_LINE_SMOOTH_HINT, GL_DONT_CARE);
    glEnable( GL_BLEND );
    glBlendFunc( GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA );
    glEnable(GL_LINE_SMOOTH);
    glEnable(GL_TEXTURE_2D);
    
    GLuint buffer[2];
    glGenBuffers(2, buffer);
    glBindBuffer(GL_ARRAY_BUFFER, buffer[0]);

    // Abaixo, nós enviamos todo o conteúdo da variável vertices.

    std::vector< glm::vec3 > v_vertices;  //Vetor de coordenadas de vertices do cenario
    std::vector< glm::vec2 > v_uvs;       //Vetor de coordenadas de textura do cenario 
    std::vector< glm::vec3 > v_normals;   //Vetor de normais do cenario (nao usado neste trabalho!!)


    std::vector<texture_info> textures; //Vetor auxiliar de informacoes de texturas usadas na malha

    //Criacao do modelo da malha de cabana com suas respectivas texturas
    textures.push_back({"cabana/WoodCabinDif.jpg",GL_RGB});
    textures.push_back({"cabana/WoodCabinDif.jpg",GL_RGB});
    mesh cabana(program, "cabana/cabana.obj", textures, v_vertices, v_normals, v_uvs);
    textures.clear();

    //Criacao do modelo da malha do terreno externo de areia com sua respectiva textura
    textures.push_back({"terreno/areia.jpg", GL_RGB});
    mesh terreno1(program, "terreno/terreno.obj", textures, v_vertices, v_normals, v_uvs);
    textures.clear();



    //Envia o vetor de coordenadas dos vertices do cenario para a GPU
    glBufferData(GL_ARRAY_BUFFER, v_vertices.size() * sizeof(glm::vec3), &v_vertices[0], GL_STATIC_DRAW);
    GLint loc = glGetAttribLocation(program, "position");
    glEnableVertexAttribArray(loc);
    glVertexAttribPointer(loc, 3, GL_FLOAT, GL_FALSE, sizeof(glm::vec3), (void*) 0); // https://www.khronos.org/registry/OpenGL-Refpages/gl4/html/glVertexAttribPointer.xhtml
    
    //Envia o vetor de coordenadas de textura do cenario para a GPU
    glBindBuffer(GL_ARRAY_BUFFER, buffer[1]);
    glBufferData(GL_ARRAY_BUFFER, v_uvs.size() * sizeof(glm::vec2), &v_uvs[0], GL_STATIC_DRAW);
    GLint loc_texture_coord = glGetAttribLocation(program, "texture_coord");
    glEnableVertexAttribArray(loc_texture_coord);
    glVertexAttribPointer(loc_texture_coord, 2, GL_FLOAT, GL_FALSE, sizeof(glm::vec2), (void*) 0);
    
    //Indica quantos vertices esse cenario possui no total
    std::cout<< std::endl<<"Este cenario possui: "<<v_vertices.size()<<" vertices"<<std::endl;


    // Exibindo nossa janela
    glfwShowWindow(window);

    //glfwSetCursorPos(window, 500.0, 500.0);

    glEnable(GL_DEPTH_TEST);// ### importante para 3D

    //Inicializa o objeto de camera responsavel por criar as matrizes VIEW e PROJECTION do pipeline MVP
    camera Cam(program, glm::vec3(0.0,5.0,10.0), cameraFront, glm::vec3(0.0,1.0,0.0), 45, 1.0f, 0.1f, 100.0f, true);

    float angle = 0;            //Angulo responsavel pela movimentacao em circulos do modelo do cachorro
    float angle_inc = 0.5;      

    while (!glfwWindowShouldClose(window) && !stop)
    {   
        glfwPollEvents();
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
        glClearColor(1.0, 1.0, 1.0, 1.0);

        //Ativa ou desativa o modo poligono segundo a especificacao do trabalho
        if(polygonMode){
            glPolygonMode(GL_FRONT_AND_BACK,GL_LINE);
        }
        else{
            glPolygonMode(GL_FRONT_AND_BACK,GL_FILL);
        }

        //Calcula quanto tempo se passou entre o ultimo frame e o atual
        float currentFrame = glfwGetTime();
        deltaTime = currentFrame - lastFrame;
        lastFrame = currentFrame;  

        cursor_position_update(window); //Chama a funcao que le as coordenadas do mouse e obtem para onde a camera deve olhar 

        //Movimenta a camera pelo cenario
        if(W){  //Para frente
            Cam.moveFront(deltaTime);
            W = false;
        }
        if(S){  //Para tras
            Cam.moveBack(deltaTime);
            S = false;
        }
        if(A){  //Para a esquerda
            Cam.moveLeft(deltaTime);
            A = false;
        }
        if(D){  //Para a direita
            Cam.moveRight(deltaTime);
            D = false;
        }


        Cam.setFront(cameraFront);  //set para onde a camera deve olhar, calculado pela funcao de leitura do mouse
        Cam.update();               //atualiza e manda os valores das matrizes calculadas pelo objeto de camera para a GPU (VIEW e PROJECTION)

        //Posicionamento dos modelos no cenario e desenha cada objeto
        cabana.scale(0.1f,0.1f,0.1f);
        cabana.update();


        terreno1.scale(15.0f,15.0f,15.0f);
        terreno1.update();

        glfwSwapBuffers(window);
        
    }

    glfwDestroyWindow(window);
    
    glfwTerminate();
    exit(EXIT_SUCCESS);
}