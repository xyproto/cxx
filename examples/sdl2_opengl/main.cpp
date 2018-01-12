/*
 *
 * SDL2 + OpenGL 3.2 example
 *
 * Based on:
 *     http://headerphile.com/sdl2/opengl-part-1-sdl-opengl-awesome/
 * Which is based on:
 *     https://www.opengl.org/wiki/Tutorial1:_Creating_a_Cross_Platform_OpenGL_3.2_Context_in_SDL_(C_/_SDL)
 *
 * Press "r", "g" or "b" to change color.
 *
 */

// C++ Headers
#include <iostream>
#include <string>

// OpenGL / glew Headers
#define GL3_PROTOTYPES 1
#include <GL/glew.h>

// SDL2 Headers
#include <SDL2/SDL.h>

std::string programName = "Headerphile SDL2 - OpenGL thing";

// Our SDL_Window ( just like with SDL2 wihout OpenGL)
SDL_Window* mainWindow;

// Our opengl context handle
SDL_GLContext mainContext;

bool SetOpenGLAttributes();
void Print_OpenGL_Version();
void CheckSDLError(int line);
void RunGame();
void Cleanup();

bool Init() {
    // Initialize SDL's Video subsystem
    if (SDL_Init(SDL_INIT_VIDEO) < 0) {
        std::cout << "Failed to init SDL\n";
        return false;
    }

    // Create our window centered at 512x512 resolution
    mainWindow =
        SDL_CreateWindow(programName.c_str(), SDL_WINDOWPOS_CENTERED,
                         SDL_WINDOWPOS_CENTERED, 512, 512, SDL_WINDOW_OPENGL);

    // Check that everything worked out okay
    if (!mainWindow) {
        std::cout << "Unable to create window\n";
        CheckSDLError(__LINE__);
        return false;
    }

    // Create our opengl context and attach it to our window
    mainContext = SDL_GL_CreateContext(mainWindow);

    SetOpenGLAttributes();

    // This makes our buffer swap syncronized with the monitor's vertical
    // refresh
    SDL_GL_SetSwapInterval(1);

// Init GLEW
// Apparently, this is needed for Apple. Thanks to Ross Vander for letting me
// know
#ifndef __APPLE__
    glewExperimental = GL_TRUE;
    glewInit();
#endif

    return true;
}

bool SetOpenGLAttributes() {
    // Set our OpenGL version.
    // SDL_GL_CONTEXT_CORE gives us only the newer version, deprecated functions
    // are disabled
    SDL_GL_SetAttribute(SDL_GL_CONTEXT_PROFILE_MASK,
                        SDL_GL_CONTEXT_PROFILE_CORE);

    // 3.2 is part of the modern versions of OpenGL, but most video cards whould
    // be able to run it
    SDL_GL_SetAttribute(SDL_GL_CONTEXT_MAJOR_VERSION, 3);
    SDL_GL_SetAttribute(SDL_GL_CONTEXT_MINOR_VERSION, 2);

    // Turn on double buffering with a 24bit Z buffer.
    // You may need to change this to 16 or 32 for your system
    SDL_GL_SetAttribute(SDL_GL_DOUBLEBUFFER, 1);

    return true;
}

int main(int argc, char* argv[]) {
    if (!Init())
        return -1;

    Print_OpenGL_Version();
    std::cout << "Press r, g, b or Escape" << std::endl;
    std::cout.flush();

    // Clear our buffer with a black background
    // This is the same as :
    // 		SDL_SetRenderDrawColor(&renderer, 255, 0, 0, 255);
    // 		SDL_RenderClear(&renderer);
    //
    glClearColor(0.0, 0.0, 0.0, 1.0);
    glClear(GL_COLOR_BUFFER_BIT);
    SDL_GL_SwapWindow(mainWindow);

    RunGame();

    Cleanup();

    return 0;
}

void RunGame() {
    bool loop = true;

    while (loop) {
        SDL_Event event;
        while (SDL_PollEvent(&event)) {
            if (event.type == SDL_QUIT)
                loop = false;

            if (event.type == SDL_KEYDOWN) {
                switch (event.key.keysym.sym) {
                case SDLK_ESCAPE:
                case SDLK_q:
                    loop = false;
                    break;
                case SDLK_r:
                    // Cover with red and update
                    glClearColor(1.0, 0.0, 0.0, 1.0);
                    glClear(GL_COLOR_BUFFER_BIT);
                    SDL_GL_SwapWindow(mainWindow);
                    break;
                case SDLK_g:
                    // Cover with green and update
                    glClearColor(0.0, 1.0, 0.0, 1.0);
                    glClear(GL_COLOR_BUFFER_BIT);
                    SDL_GL_SwapWindow(mainWindow);
                    break;
                case SDLK_b:
                    // Cover with blue and update
                    glClearColor(0.0, 0.0, 1.0, 1.0);
                    glClear(GL_COLOR_BUFFER_BIT);
                    SDL_GL_SwapWindow(mainWindow);
                    break;
                default:
                    break;
                }
            }
        }

        // Swap our back buffer to the front
        // This is the same as :
        // 		SDL_RenderPresent(&renderer);
    }
}

void Cleanup() {
    // Delete our OpengL context
    SDL_GL_DeleteContext(mainContext);

    // Destroy our window
    SDL_DestroyWindow(mainWindow);

    // Shutdown SDL 2
    SDL_Quit();
}

void CheckSDLError(int line = -1) {
    std::string error = SDL_GetError();

    if (error != "") {
        std::cout << "SLD Error : " << error << std::endl;

        if (line != -1)
            std::cout << "\nLine : " << line << std::endl;

        SDL_ClearError();
    }
}

void Print_OpenGL_Version() {
    int major = 0;
    SDL_GL_GetAttribute(SDL_GL_CONTEXT_MAJOR_VERSION, &major);

    int minor = 0;
    SDL_GL_GetAttribute(SDL_GL_CONTEXT_MINOR_VERSION, &minor);

    std::cout << "OpenGL " << major << "." << minor << std::endl;
}
