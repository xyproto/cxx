// Based on unlicensed sample code by Harry Lundstrom
// https://github.com/lundstroem/synth-samples-sdl2

#include "synth.h"
#include <SDL2/SDL.h>

int main()
{
    init_data();
    setup_sdl();
    setup_sdl_audio();

    SDL_Event event;

    while (true) {

        // check for SDL2 events, such as key presses
        if (check_sdl_events(event)) {
            
            // quit
            quit_audio = true;
            break;
        }

        SDL_Delay(16);
    }

    cleanup_data();
    destroy_sdl();
    SDL_CloseAudioDevice(audio_device);
    SDL_Quit();

    return 0;
}
