import org.lwjgl.*;
import org.lwjgl.glfw.*;
import org.lwjgl.opengl.*;
import java.nio.*;
import static org.lwjgl.glfw.GLFW.*;
import static org.lwjgl.opengl.GL45.*;
import static org.lwjgl.system.MemoryUtil.*;

public class Main {


    public void run() {
        // inicicializando o sistema de janelas
        glfwInit();

        // deixando a janela invisivel, por enquanto
        glfwWindowHint(GLFW_VISIBLE, GLFW_FALSE);


        // criando uma janela
        long window = glfwCreateWindow(800, 800, "Minha Janela", NULL, NULL);


        // tornando a janela como principal 
        glfwMakeContextCurrent(window);
        GL.createCapabilities(); // isso eh especifico para Java!


        // GLSL para Vertex Shader
        String vertex_code =
        "attribute vec2 position;\n" +
        "void main()\n" +
        "{\n" +
        "    gl_Position = vec4(position, 0.0, 1.0);\n" +
        "}\n";

        // GLSL para Fragment Shader
        String fragment_code =
        "uniform vec4 color;\n" +
        "void main()\n" +
        "{\n" +
        "    gl_FragColor = vec4(1.0, 0.0, 0.0, 1.0);\n" +
        "}\n";

        // Requisitando slot para a GPU para nossos programas Vertex e Fragment Shaders
        int program = glCreateProgram();
        int vertex = glCreateShader(GL_VERTEX_SHADER);
        int fragment = glCreateShader(GL_FRAGMENT_SHADER);

        // Associando nosso código-fonte GLSL aos slots solicitados
        glShaderSource(vertex, vertex_code);
        glShaderSource(fragment, fragment_code);

        // Compilando o Vertex Shader e verificando erros
        glCompileShader(vertex);

        int[] isCompiled = new int[1];
        glGetShaderiv(vertex, GL_COMPILE_STATUS, isCompiled);
        if(isCompiled[0] == GL_FALSE){
            
            System.out.println("Erro de compilacao no Vertex Shader.\n");
            System.out.println(glGetShaderInfoLog(vertex));

        }

        // Compilando o Fragment Shader e verificando erros
        glCompileShader(fragment);

        isCompiled = new int[1];
        glGetShaderiv(fragment, GL_COMPILE_STATUS, isCompiled);
        if(isCompiled[0] == GL_FALSE){
            
            System.out.println("Erro de compilacao no Fragment Shader.\n");
            System.out.println(glGetShaderInfoLog(fragment));

        }

        // Associando os programas compilado ao programa principal
        glAttachShader(program, vertex);
        glAttachShader(program, fragment);

        // Linkagem do programa e definindo como default
        glLinkProgram(program);
        glUseProgram(program);


        // Preparando dados para enviar a GPU        
        FloatBuffer vertices = BufferUtils.createFloatBuffer(6);
        vertices.put(new float[] {
             0.00f, +0.05f,
            -0.05f, -0.05f,
            +0.05f, -0.05f
        }).flip();


        int buffer = glGenBuffers();
        glBindBuffer(GL_ARRAY_BUFFER, buffer);


        // Abaixo, nós enviamos todo o conteúdo da variável vertices.
        glBufferData(GL_ARRAY_BUFFER, vertices, GL_DYNAMIC_DRAW);


        // Associando variáveis do programa GLSL (Vertex Shaders) com nossos dados
        int loc = glGetAttribLocation(program, "position");
        glEnableVertexAttribArray(loc);
        glVertexAttribPointer(loc, 2, GL_FLOAT, false, 0, 0); // https://www.khronos.org/registry/OpenGL-Refpages/gl4/html/glVertexAttribPointer.xhtml

        // Exibindo nossa janela
        glfwShowWindow(window);

        while (!glfwWindowShouldClose(window))
        {



            glfwPollEvents();

            glClear(GL_COLOR_BUFFER_BIT);
            glClearColor(1.0f, 1.0f, 1.0f, 1.0f);


            glDrawArrays(GL_TRIANGLES, 0, 3);

            glfwSwapBuffers(window);

        }

        glfwDestroyWindow(window);

        glfwTerminate();
    }
    
    public static void main(String[] args) {
        new Main().run();
    }

}