#pragma once

#include <SDL2/SDL.h>
#include <memory>

using std::decay_t;
using std::forward;
using std::unique_ptr;

namespace sdl2 {

// Useful function from Eric Scott Barr.
// https://eb2.co/blog/2014/04/c-plus-plus-14-and-sdl2-managing-resources/
template <typename Creator, typename Destructor, typename... Arguments>
auto make_resource(Creator c, Destructor d, Arguments&&... args) {
    auto r = c(forward<Arguments>(args)...);
    return unique_ptr<decay_t<decltype(*r)>, decltype(d)>(r, d);
}

// make_window constructs an SDL2 Window that will be destroyed when
// deconstructed
using window_ptr_t = unique_ptr<SDL_Window, decltype(&SDL_DestroyWindow)>;
window_ptr_t make_window(const char* title, int x, int y, int w, int h,
                         Uint32 flags);

// make_renderer constructs an SDL2 Renderer that will be destroyed when
// deconstructed
using renderer_ptr_t = unique_ptr<SDL_Renderer, decltype(&SDL_DestroyRenderer)>;
renderer_ptr_t make_renderer(SDL_Window* win, int x, Uint32 flags);

// make_bmp constructs an SDL2 Surface using a BMP filename, that will be
// destroyed when deconstructed
using surf_ptr_t = unique_ptr<SDL_Surface, decltype(&SDL_FreeSurface)>;
surf_ptr_t make_bmp(SDL_RWops* sdlfile);

// make_texture constructs an SDL2 Texture given a Renderer and a Surface, that
// will be destroyed when deconstructed
using texture_ptr_t = unique_ptr<SDL_Texture, decltype(&SDL_DestroyTexture)>;
texture_ptr_t make_texture(SDL_Renderer* ren, SDL_Surface* surf);

// Clear a Renderer
void Clear(renderer_ptr_t& ren);

// Copy to a Renderer from a Texture
void Copy(renderer_ptr_t& ren, texture_ptr_t& tex);

// Present a Renderer
void Present(renderer_ptr_t& ren);

// Delay a certain number of milliseconds
void Delay(int ms);

// Return the SDL_Error, if any
const char* Error();

} // namespace sdl2
