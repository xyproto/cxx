// Based on https://gist.github.com/armornick/3497064 and
// https://stackoverflow.com/a/1641223/131264

#include <SDL2/SDL.h>
#include <SDL2/SDL_mixer.h>
#include <csignal>
#include <cstdlib>
#include <iostream>
#include <unistd.h>

// RESOURCEDIR is defined by cxx, so that the path will be correct both at development-time
// and at installation-time

#define WAV_PATH RESOURCEDIR "Roland-GR-1-Trumpet-C5.wav"
#define MUS_PATH RESOURCEDIR "HR2_Friska.ogg"

// Wave file
Mix_Chunk* wave = NULL;

// Music file
Mix_Music* music = NULL;

// Interrupted?
bool interrupted = false;

// Signal handler
void my_handler(int s) { interrupted = true; }

int main(int argc, char* argv[])
{

    // Initialize SDL2
    if (SDL_Init(SDL_INIT_AUDIO) < 0) {
        return -1;
    }

    // Prepare my_handler as a signal handler
    struct sigaction sigIntHandler;
    sigIntHandler.sa_handler = my_handler;
    sigemptyset(&sigIntHandler.sa_mask);
    sigIntHandler.sa_flags = 0;

    // Set up a signal handler for ctrl-c
    sigaction(SIGINT, &sigIntHandler, NULL);

    // Initialize SDL_mixer
    if (Mix_OpenAudio(22050, MIX_DEFAULT_FORMAT, 2, 4096) == -1) {
        return -1;
    }

    // Load the sound effect sample
    wave = Mix_LoadWAV(WAV_PATH);
    if (wave == NULL) {
        return -1;
    }

    // Load the music sample
    music = Mix_LoadMUS(MUS_PATH);
    if (music == NULL) {
        return -1;
    }

    if (Mix_PlayChannel(-1, wave, 0) == -1) {
        return -1;
    }

    if (Mix_PlayMusic(music, -1) == -1) {
        return -1;
    }

    // Play while not interrupted by ctrl-c
    while (Mix_PlayingMusic()) {
        if (interrupted) {
            std::cout << std::endl;
            break;
        }
    }

    // Free the memory
    Mix_FreeChunk(wave);
    Mix_FreeMusic(music);

    // Quit SDL_Mixer
    Mix_CloseAudio();

    // Friendly message at the end
    if (interrupted) {
        std::cout << "Bye!" << std::endl;
        return 1;
    }

    return 0;
}
