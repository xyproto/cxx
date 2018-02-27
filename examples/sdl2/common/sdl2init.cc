#include "sdl2init.h"
#include <SDL2/SDL.h>

namespace sdl2 {

Init::Init() {
  _initialized = (SDL_Init(SDL_INIT_EVERYTHING) == 0);
}

Init::~Init() {
  SDL_Quit();
  _initialized = false;
}

bool Init::Initialized() {
  return _initialized;
}

}  // namespace sdl2
