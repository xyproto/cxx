#pragma once

#include <X11/Xlib.h>
#include <string>

using namespace std::string_literals;

namespace X {

// Undefine the RootWindow macro, since it collides with the Window class
//#define RootWindow(dpy, scr)  (ScreenOfDisplay(dpy,scr)->root)
#undef RootWindow

// Class that wraps an X11 Display and an X11 Window
class Window {
private:
    ::Display* _d;
    ::Window _window;
    ::Atom _wmDeleteMessage;

public:
    Window(int x, int y, unsigned int w, unsigned int h, std::string name = ""s);
    ~Window();
    int Screen();
    int RootWindow();
    void NewWindow();
    ::GC GC();
    void SelectInput();
    void MapWindow();
    ::Window GetWindow();
    ::Display* GetDisplay();
    void FillRectangle(int x, int y, unsigned int w, unsigned int h);
    void DrawString(int x, int y, std::string msg);
    bool WindowCloseMessage(const unsigned long msg);
};

} // namespace X
