#include "x.h"

#include <X11/Xlib.h>
#include <iostream>
#include <stdexcept>
#include <string>
#include <thread>

using namespace std::string_literals;

namespace X {

// Undefine the RootWindow macro, since it collides with the Window class
//#define RootWindow(dpy, scr)  (ScreenOfDisplay(dpy,scr)->root)
#undef RootWindow

Window::Window(int x, int y, unsigned int w, unsigned int h, std::string name)
{
    if (name.length() > 0) {
        _d = XOpenDisplay(name.c_str());
    } else {
        _d = XOpenDisplay(nullptr);
    }
    if (_d == nullptr) {
        throw std::runtime_error("failed to construct an X11 Display"s);
    }

    // Create a window too.
    // TODO: Error handling
    _window = XCreateSimpleWindow(_d, this->RootWindow(), x, y, w, h, 1,
        BlackPixel(_d, this->Screen()), WhitePixel(_d, this->Screen()));

    // Listen for window close events
    _wmDeleteMessage = XInternAtom(_d, "WM_DELETE_WINDOW", false);
    XSetWMProtocols(_d, _window, &_wmDeleteMessage, 1);

    std::cout << "Window constructed"s << std::endl;
}

Window::~Window()
{
    XCloseDisplay(_d);

    std::cout << "Window deconstructed"s << std::endl;
}

int Window::Screen() { return DefaultScreen(_d); }

int Window::RootWindow() { return ScreenOfDisplay(_d, this->Screen())->root; }

GC Window::GC() { return DefaultGC(_d, this->Screen()); }

void Window::SelectInput()
{
    XSelectInput(_d, _window, ExposureMask | KeyPressMask | ButtonPressMask);
}

void Window::MapWindow() { XMapWindow(_d, _window); }

::Window Window::GetWindow() { return _window; }

::Display* Window::GetDisplay() { return _d; }

void Window::FillRectangle(int x, int y, unsigned int w, unsigned int h)
{
    // TODO: save the gc in an object variable
    XFillRectangle(_d, _window, this->GC(), x, y, w, h);
}

void Window::DrawString(int x, int y, std::string msg)
{
    // TODO: save the gc in an object variable
    XDrawString(_d, _window, this->GC(), x, y, msg.c_str(), msg.length());
}

bool Window::WindowCloseMessage(const unsigned long msg) { return (msg == _wmDeleteMessage); }

} // namespace X
