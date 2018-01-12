#include "sdl2wrap.h"
#include <SDL2/SDL.h>
#include <memory>

using std::decay_t;
using std::forward;
using std::unique_ptr;

namespace sdl2 {

// Create a windows (unique_ptr with both a window and the destructor)
window_ptr_t make_window(const char* title, int x, int y, int w, int h,
                         Uint32 flags) {
    return make_resource(SDL_CreateWindow, SDL_DestroyWindow, title, x, y, w, h,
                         flags);
}

// Create a renderer given a window, containing both the renderer and the
// destructor
renderer_ptr_t make_renderer(SDL_Window* win, int x, Uint32 flags) {
    return make_resource(SDL_CreateRenderer, SDL_DestroyRenderer, win, x,
                         flags);
}

// Create a surface from a bmp file, containing both the surface and the
// destructor
surf_ptr_t make_bmp(SDL_RWops* sdlfile) {
    // May throw an exception if sdlfile is nullptr
    return make_resource(SDL_LoadBMP_RW, SDL_FreeSurface, sdlfile, 1);
}

// Create a texture from a renderer and a surface
texture_ptr_t make_texture(SDL_Renderer* ren, SDL_Surface* surf) {
    return make_resource(SDL_CreateTextureFromSurface, SDL_DestroyTexture, ren,
                         surf);
}

// Clear a Renderer
void Clear(renderer_ptr_t& ren) { SDL_RenderClear(ren.get()); }

// Copy to a Renderer from a Texture
void Copy(renderer_ptr_t& ren, texture_ptr_t& tex) {
    SDL_RenderCopy(ren.get(), tex.get(), nullptr, nullptr);
}

// Present a Renderer
void Present(renderer_ptr_t& ren) { SDL_RenderPresent(ren.get()); }

// Delay a certain number of milliseconds
void Delay(int ms) { SDL_Delay(ms); }

// Return the SDL_Error, if any
const char* Error() { return SDL_GetError(); }

} // namespace sdl2
