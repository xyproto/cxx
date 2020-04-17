// Based on this forum post by @palmer789:
// https://discourse.glfw.org/t/opengl-es3-0-with-glfw-on-pc/186/19

#include <GL/glew.h>
#define GLFW_INCLUDE_DLL
#define GLFW_INCLUDE_NONE
#include <GLFW/glfw3.h>
#include <iostream>

// Vertex shader
static const char* vShaderStr = R"(
#version 300 es
layout(location = 0) in vec4 vPosition;
void main() {
    gl_Position = vPosition;
}
)";

// Fragment shader
static const char* fShaderStr = R"(
#version 300 es
precision mediump float;
out vec4 fragColor;
void main() {
    fragColor = vec4 ( 1.0, 0.0, 0.0, 1.0 );
}
)";

GLuint g_programObject;

GLuint LoadShader(GLenum type, const char* shaderSrc)
{
    GLuint shader;
    GLint compiled;

    // Create the shader object
    shader = glCreateShader(type);
    if (shader == 0) {
        return 0;
    }

    // Load the shader source
    glShaderSource(shader, 1, &shaderSrc, nullptr);

    // Compile the shader
    glCompileShader(shader);

    // Check the compile status
    glGetShaderiv(shader, GL_COMPILE_STATUS, &compiled);

    if (!compiled) {
        GLint infoLen = 0;
        glGetShaderiv(shader, GL_INFO_LOG_LENGTH, &infoLen);
        if (infoLen > 1) {
            char* infoLog = (char*)malloc(sizeof(char) * infoLen);
            glGetShaderInfoLog(shader, infoLen, nullptr, infoLog);
            free(infoLog);
        }
        glDeleteShader(shader);
        return 0;
    }

    return shader;
}

bool Init()
{
    GLuint vertexShader;
    GLuint fragmentShader;
    GLuint programObject;
    GLint linked;

    // Load the vertex/fragment shaders
    vertexShader = LoadShader(GL_VERTEX_SHADER, vShaderStr);
    fragmentShader = LoadShader(GL_FRAGMENT_SHADER, fShaderStr);

    // Create the program object
    programObject = glCreateProgram();

    if (programObject == 0) {
        return 0;
    }

    glAttachShader(programObject, vertexShader);
    glAttachShader(programObject, fragmentShader);

    // Link the program
    glLinkProgram(programObject);

    // Check the link status
    glGetProgramiv(programObject, GL_LINK_STATUS, &linked);

    if (!linked) {
        GLint infoLen = 0;
        glGetProgramiv(programObject, GL_INFO_LOG_LENGTH, &infoLen);
        if (infoLen > 1) {
            char* infoLog = (char*)malloc(sizeof(char) * infoLen);
            glGetProgramInfoLog(programObject, infoLen, nullptr, infoLog);
            free(infoLog);
        }
        glDeleteProgram(programObject);
        return false;
    }

    // Store the program object
    g_programObject = programObject;
    glClearColor(1.0f, 1.0f, 1.0f, 0.0f);
    return true;
}

static void error_callback(int error, const char* description) { fputs(description, stderr); }

static void key_callback(GLFWwindow* window, int key, int scancode, int action, int mods)
{
    if (key == GLFW_KEY_ESCAPE && action == GLFW_PRESS) {
        glfwSetWindowShouldClose(window, GL_TRUE);
    }
}

int main(int argc, char* argv[])
{
    GLFWwindow* window;

    glfwSetErrorCallback(error_callback);
    if (!glfwInit())
        exit(EXIT_FAILURE);

    glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 3);
    glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 0);
    glfwWindowHint(GLFW_CLIENT_API, GLFW_OPENGL_ES_API);

    window = glfwCreateWindow(640, 480, "OpenGL ES 3 + GLFW", nullptr, nullptr);

    // int result =
    glfwGetWindowAttrib(window, GLFW_CLIENT_API);

    if (!window) {
        glfwTerminate();
        exit(EXIT_FAILURE);
    }

    glfwMakeContextCurrent(window);
    glfwSwapInterval(1);
    glfwSetKeyCallback(window, key_callback);

    // start GLEW extension handler
    glewExperimental = GL_TRUE;
    glewInit();

    std::cout << glGetString(GL_VERSION) << std::endl;

    if (!Init()) {
        return 0;
    }

    while (!glfwWindowShouldClose(window)) {
        int width, height;
        glfwGetFramebufferSize(window, &width, &height);
        // float ratio = width / (float) height;

        GLfloat vVertices[] = { 0.0f, 0.5f, 0.0f, -0.5f, -0.5f, 0.0f, 0.5f, -0.5f, 0.0f };

        glViewport(0, 0, width, height);

        glClear(GL_COLOR_BUFFER_BIT);

        // Use the program object
        glUseProgram(g_programObject);

        // Load the vertex data
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, vVertices);
        glEnableVertexAttribArray(0);

        glDrawArrays(GL_TRIANGLES, 0, 3);

        glfwSwapBuffers(window);
        glfwPollEvents();
    }

    glfwDestroyWindow(window);
    glfwTerminate();
    exit(EXIT_SUCCESS);
}
