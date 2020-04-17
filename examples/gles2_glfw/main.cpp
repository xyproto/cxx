// OpenGL ES 2.0 example
// Thanks Ciro Santilli @ https://stackoverflow.com/a/39356268/131264

#define GLFW_INCLUDE_ES2
#include <GLFW/glfw3.h>
#include <iostream>

static const GLuint WIDTH = 800;
static const GLuint HEIGHT = 600;

static const GLchar* g_vertex_shader_source = R"(
    #version 100
    attribute vec3 position;
    void main() {
       gl_Position = vec4(position, 1.0);
    }
)";

static const GLchar* g_fragment_shader_source = R"(
    #version 100
    void main() {
       gl_FragColor = vec4(1.0, 0.0, 0.0, 1.0);
    }
)";

static const GLfloat vertices[] = {
    0.0f,
    0.5f,
    0.0f,
    0.5f,
    -0.5f,
    0.0f,
    -0.5f,
    -0.5f,
    0.0f,
};

GLint common_get_shader_program(
    const char* vertex_shader_source, const char* fragment_shader_source)
{
    enum Consts { INFOLOG_LEN = 512 };
    GLchar infoLog[INFOLOG_LEN];
    GLint fragment_shader;
    GLint shader_program;
    GLint success;
    GLint vertex_shader;

    /* Vertex shader */
    vertex_shader = glCreateShader(GL_VERTEX_SHADER);
    glShaderSource(vertex_shader, 1, &g_vertex_shader_source, nullptr);
    glCompileShader(vertex_shader);
    glGetShaderiv(vertex_shader, GL_COMPILE_STATUS, &success);
    if (!success) {
        glGetShaderInfoLog(vertex_shader, INFOLOG_LEN, nullptr, infoLog);
        std::cerr << "ERROR::SHADER::VERTEX::COMPILATION_FAILED" << std::endl
                  << infoLog << std::endl;
    }

    /* Fragment shader */
    fragment_shader = glCreateShader(GL_FRAGMENT_SHADER);
    glShaderSource(fragment_shader, 1, &g_fragment_shader_source, nullptr);
    glCompileShader(fragment_shader);
    glGetShaderiv(fragment_shader, GL_COMPILE_STATUS, &success);
    if (!success) {
        glGetShaderInfoLog(fragment_shader, INFOLOG_LEN, nullptr, infoLog);
        std::cerr << "ERROR::SHADER::FRAGMENT::COMPILATION_FAILED" << std::endl
                  << infoLog << std::endl;
    }

    /* Link shaders */
    shader_program = glCreateProgram();
    glAttachShader(shader_program, vertex_shader);
    glAttachShader(shader_program, fragment_shader);
    glLinkProgram(shader_program);
    glGetProgramiv(shader_program, GL_LINK_STATUS, &success);
    if (!success) {
        glGetProgramInfoLog(shader_program, INFOLOG_LEN, nullptr, infoLog);
        std::cerr << "ERROR::SHADER::PROGRAM::LINKING_FAILED" << std::endl << infoLog << std::endl;
    }

    glDeleteShader(vertex_shader);
    glDeleteShader(fragment_shader);
    return shader_program;
}

int main(void)
{
    GLuint shader_program, vbo;
    GLint pos;
    GLFWwindow* window;

    glfwInit();
    glfwWindowHint(GLFW_CLIENT_API, GLFW_OPENGL_ES_API);
    glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 2);
    glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 0);
    window = glfwCreateWindow(WIDTH, HEIGHT, "OpenGL ES 2 + GLFW", nullptr, nullptr);
    glfwMakeContextCurrent(window);

    std::cout << "GL_VERSION  : " << glGetString(GL_VERSION) << std::endl;
    std::cout << "GL_RENDERER : " << glGetString(GL_RENDERER) << std::endl;

    shader_program = common_get_shader_program(g_vertex_shader_source, g_fragment_shader_source);
    pos = glGetAttribLocation(shader_program, "position");

    glClearColor(0.0f, 0.0f, 0.0f, 1.0f);
    glViewport(0, 0, WIDTH, HEIGHT);

    glGenBuffers(1, &vbo);
    glBindBuffer(GL_ARRAY_BUFFER, vbo);
    glBufferData(GL_ARRAY_BUFFER, sizeof(vertices), vertices, GL_STATIC_DRAW);
    glVertexAttribPointer(pos, 3, GL_FLOAT, GL_FALSE, 0, (GLvoid*)0);
    glEnableVertexAttribArray(pos);
    glBindBuffer(GL_ARRAY_BUFFER, 0);

    while (!glfwWindowShouldClose(window)) {
        glfwPollEvents();
        glClear(GL_COLOR_BUFFER_BIT);
        glUseProgram(shader_program);
        glDrawArrays(GL_TRIANGLES, 0, 3);
        glfwSwapBuffers(window);
    }
    glDeleteBuffers(1, &vbo);
    glfwTerminate();
    return EXIT_SUCCESS;
}
