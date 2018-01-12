#include "sdl2init.h"
#include "sdl2wrap.h"
#include <iostream>

int main() {
    using std::cout;
    using std::endl;

    sdl2::Init sys;
    if (!sys.Initialized()) {
        cout << "Error initializing SDL2: " << sdl2::Error() << endl;
        return 1;
    }

    auto win = sdl2::make_window("Hello, World!", 100, 100, 960, 540,
                                 SDL_WINDOW_SHOWN);
    if (win.get() == nullptr) {
        cout << "Error creating window: " << sdl2::Error() << endl;
        return 1;
    }

    auto ren = sdl2::make_renderer(
        win.get(), -1, SDL_RENDERER_ACCELERATED | SDL_RENDERER_PRESENTVSYNC);
    if (ren.get() == nullptr) {
        cout << "Error creating renderer: " << sdl2::Error() << endl;
        return 1;
    }

    auto file = SDL_RWFromFile(IMGDIR "sake.bmp", "rb");
    if (file == nullptr) {
        cout << "Error reading file: " << sdl2::Error() << endl;
        return 1;
    }

    auto bmp = sdl2::make_bmp(file);
    if (bmp.get() == nullptr) {
        cout << "Error creating surface: " << sdl2::Error() << endl;
        return 1;
    }

    auto tex = sdl2::make_texture(ren.get(), bmp.get());
    if (tex.get() == nullptr) {
        cout << "Error creating texture: " << sdl2::Error() << endl;
        return 1;
    }

    for (auto i = 0; i < 100; ++i) {
        sdl2::Clear(ren);
        sdl2::Copy(ren, tex);
        sdl2::Present(ren);
        sdl2::Delay(50);
    }

    return 0;
}
