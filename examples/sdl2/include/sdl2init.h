#pragma once

namespace sdl2 {

// Init is a class to keep track of if SDL2 has been initialized or not
class Init {
   private:
    bool _initialized = false;

   public:
    Init();
    ~Init();
    bool Initialized();

};  // class System

}  // namespace sdl2
