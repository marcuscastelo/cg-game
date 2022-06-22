#include "mesh.hpp"
#include <iostream>

////////////////uso exclusivo para abrir imagens de textura//////////////////////
#include <SDL2/SDL.h>
#include <SDL2/SDL_image.h>
/////////////////////////////////////////////////////////////////////////////////
#include <stdio.h>
#include <string.h>

//Baseada na funcao do respectivo link, entretanto fora realizadas melhorias e adaptacoes ao codigo!
//http://www.opengl-tutorial.org/beginners-tutorials/tutorial-7-model-loading/
//Funcao para a leitura do arquivo .obj
bool loadOBJ(const char * path, std::vector < glm::vec3 > & out_vertices, std::vector < glm::vec2 > & out_uvs, std::vector < glm::vec3 > & out_normals, std::vector<int>& texture_groups){
    std::vector< unsigned int > vertexIndices, uvIndices, normalIndices;
    std::vector< glm::vec3 > temp_vertices;
    std::vector< glm::vec2 > temp_uvs;
    std::vector< glm::vec3 > temp_normals;

    int n_group_vertices = 0;   //quantos vertices tem cada grupo
    bool firstGroup = true;     //se eh o primeiro grupo de vertices


    FILE * file = fopen(path, "r"); //Abre o arquivo .obj para leitura
    if(file == NULL){
        std::cout << "Erro ao abrir o arquivo\n";
        return false;
    } 


    while(1){
        char lineHeader[128];
        int res = fscanf(file, "%s", lineHeader); //Le a primeira instrucao da linha
        
        if (res == EOF){ //Se chegou ao fim do arquivo
            break; 
        }

        if (strcmp(lineHeader, "v") == 0){ //Se for coordenada de vertice
            glm::vec3 vertex;
            fscanf(file, "%f %f %f\n", &vertex.x, &vertex.y, &vertex.z );
            temp_vertices.push_back(vertex);
        }
        else if ( strcmp( lineHeader, "vt" ) == 0 ){ //Se for coordenada de textura
            glm::vec2 uv;
            fscanf(file, "%f %f\n", &uv.x, &uv.y );
            temp_uvs.push_back(uv);
        }
        else if ( strcmp( lineHeader, "vn" ) == 0 ){ //Se for coordenada de normal
            glm::vec3 normal;
            fscanf(file, "%f %f %f\n", &normal.x, &normal.y, &normal.z );
            temp_normals.push_back(normal);
        }
        else if ( strcmp( lineHeader, "f" ) == 0 ){ //Se for face
            std::string vertex1, vertex2, vertex3;
            unsigned int vertexIndex[3], uvIndex[3], normalIndex[3];
            
            long int before_position = ftell(file);
            int matches = fscanf(file, "%d/%d/%d %d/%d/%d %d/%d/%d\n", &vertexIndex[0], &uvIndex[0], &normalIndex[0], &vertexIndex[1], &uvIndex[1], &normalIndex[1], &vertexIndex[2], &uvIndex[2], &normalIndex[2] );
            if (matches != 9){ //Se o formato nao possuir as coordenadas de normal
                fseek(file, before_position, SEEK_SET);
                fscanf(file, "%d/%d %d/%d %d/%d\n", &vertexIndex[0], &uvIndex[0], &vertexIndex[1], &uvIndex[1], &vertexIndex[2], &uvIndex[2]);
            }
            vertexIndices.push_back(vertexIndex[0]);  //Vetores auxiliares de indices
            vertexIndices.push_back(vertexIndex[1]);
            vertexIndices.push_back(vertexIndex[2]);
            uvIndices    .push_back(uvIndex[0]);
            uvIndices    .push_back(uvIndex[1]);
            uvIndices    .push_back(uvIndex[2]);
            normalIndices.push_back(normalIndex[0]);
            normalIndices.push_back(normalIndex[1]);
            normalIndices.push_back(normalIndex[2]);
            n_group_vertices += 3;
        }
        else if(strcmp( lineHeader, "g" ) == 0 || strcmp( lineHeader, "usemtl" ) == 0){ //Se for um grupo de textura
            if(firstGroup){     //Se primeiro grupo ainda nao realiza a insercao, pois nao ha o que inserir
                firstGroup = false;
            }
            else{
                texture_groups.push_back(n_group_vertices); //Insere no vetor o numero de vertices que o grupo de textura
                n_group_vertices = 0; 
            }
        }
    }

    //push do ultimo ou unico grupo de vertices
    texture_groups.push_back(n_group_vertices);

    //Insere no vetor de vertices do cenario os vertices relativos a cada face segundo o vetor de indices de cada face
    for(unsigned int i=0; i < vertexIndices.size(); i++){
        unsigned int vertexIndex = vertexIndices[i];
        glm::vec3 vertex = temp_vertices[ vertexIndex-1 ];
        out_vertices.push_back(vertex);
    }

    //Insere no vetor de coordenadas de textura relativos a cada face segundo o vetor de indices de cada face
    for(unsigned int i=0; i < uvIndices.size(); i++){
        unsigned int uvIndex = uvIndices[i];
        glm::vec2 uv = temp_uvs[ uvIndex-1 ];
        out_uvs.push_back(uv);
    }

    fclose(file);
    return true;
}


mesh::mesh(GLuint program, std::string filePath,std::vector<texture_info> textures, std::vector < glm::vec3 > & out_vertices, std::vector < glm::vec3 > & out_normals, std::vector < glm::vec2 > & out_uvs){
    this->filePath = filePath;
    this->program = program;
    this->m_model = glm::mat4(1.0f);
    this->firstVertice_index = out_vertices.size();
    this->texture_id = std::vector<GLuint>(textures.size());
    
    //Se houve erro em abrir o .obj joga um excecao
    if(!loadOBJ(filePath.c_str(), out_vertices, out_uvs, out_normals, this->texture_groups)){
        throw("Unable to get an object from the file");
    }

    SDL_Surface *minha_imagem;
    for(unsigned int i = 0; i < textures.size(); i++){ //para cada textura do objeto
        
        minha_imagem = IMG_Load(textures[i].texture_path.c_str()); //Abre a imagem da textura
        if(minha_imagem == NULL){
            throw("Unable to get a texture from the file");
        }

        glGenTextures(1, &this->texture_id[i]); //Gera um id para essa textura
        glBindTexture(GL_TEXTURE_2D, this->texture_id[i]); //Binda a textura na gpu
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT); //Filtros de repeticao: GL_REPEAT -> repeticao simples
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR); //Filtros de maginificao e minificacao: GL_LINEAR
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
        
        //Manda para a gpu a imagem da textura com o modo dela, se ela tem transparencia ou nao
        glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA,minha_imagem->w,minha_imagem->h,0,textures[i].format,GL_UNSIGNED_BYTE,minha_imagem->pixels);
        glBindTexture(GL_TEXTURE_2D, 0);
    }   
    this->n_vertices = out_vertices.size() - this->firstVertice_index; //Calcula o numero total de vertices do objeto
}

//Transformacao de translacao
void mesh::translate(float tx, float ty, float tz){
    this->m_model = glm::translate(this->m_model, glm::vec3(tx,ty,tz));
}

//Transformacao de rotacao
void mesh::rotate(float angle, direction d){
    angle = glm::radians(angle);
    switch (d){
        case X: //Rotacao em X
            this->m_model = glm::rotate(this->m_model, angle, glm::vec3(1.0,0.0,0.0));
            break;
        
        case Y: //Rotacao em Y
            this->m_model = glm::rotate(this->m_model, angle, glm::vec3(0.0,1.0,0.0));
            break;

        case Z: //Rotacao em Z
            this->m_model = glm::rotate(this->m_model, angle, glm::vec3(0.0,0.0,1.0));
            break;
    }
}

//Transformacao de escala
void mesh::scale(float sx, float sy, float sz){
    this->m_model = glm::scale(this->m_model, glm::vec3(sx,sy,sz));
}

//Manda a matriz de model para a gpu e desenha o objeto
void mesh::update(){
    //Manda a matriz de model para a gpu
    int loc_model = glGetUniformLocation(program, "model");
    glUniformMatrix4fv(loc_model, 1, GL_FALSE, glm::value_ptr(this->m_model));
    this->m_model = glm::mat4(1.0f); //Reseta a matriz de model para o proximo frame

    int firstIndex = this->firstVertice_index; //Index do grupo de vertices do objeto
    for(unsigned int i = 0; i < this->texture_groups.size(); i++){ //Para cada grupo de textura do objeto
        glBindTexture(GL_TEXTURE_2D, this->texture_id[i]);  //Usa a textura relativa a esse grupo
        glDrawArrays(GL_TRIANGLES, firstIndex, this->texture_groups[i]);    //Desenha o numero de vertices relativos a esse grupo
        firstIndex += this->texture_groups[i]; //Calcula o index do proximo grupo
    }
}

mesh::~mesh(){

}