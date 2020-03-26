#include "x.h"

#include <chrono>
#include <csignal>
#include <cstdlib>
#include <iostream>
#include <memory>
#include <thread>

using namespace std::string_literals;

volatile sig_atomic_t running = true;

void stop(int x)
{
    running = false;
    // Output a newline after the "^C" output
    std::cout << std::endl;
}

auto main(int argc, char** argv) -> int
{
    std::unique_ptr<X::Window> win;
    try {
        win = std::make_unique<X::Window>(10, 10, 100, 100);
    } catch (const std::runtime_error& err) {
        std::cerr << "ERROR: "s << err.what() << std::endl;
        return EXIT_FAILURE;
    }

    win->SelectInput();
    win->MapWindow();

    XEvent event;

    signal(SIGINT, stop);

    while (running) {
        // This check exists so that event-checking can be non-blocking if the program is
        // interrupted by SIGINT
        if (XPending(win->GetDisplay()) == 0) {
            std::this_thread::sleep_for(std::chrono::milliseconds(50));
            continue;
        }
        XNextEvent(win->GetDisplay(), &event);
        switch (event.type) {
        case Expose:
            win->FillRectangle(10, 10, 20, 20);
            win->DrawString(10, 50, "Hello, World!"s);
            break;
        case KeyPress:
            std::cout << "Key pressed: "s << event.xkey.keycode << std::endl;
            // Check for Esc or 'q'
            if (event.xkey.keycode == 0x09 || event.xkey.keycode == 0x18) {
                running = false;
            }
            break;
        case ButtonPress:
            switch (event.xbutton.button) {
            case 1:
                std::cout << "Left Click"s << std::endl;
                auto x = event.xbutton.x;
                auto y = event.xbutton.y;
                win->FillRectangle(x, y, 20, 20);
                break;
            }
            break;
        case ClientMessage:
            std::cout << "Client messages:"s << std::endl;
            for (const unsigned long& m : event.xclient.data.l) {
                if (win->WindowCloseMessage(m)) {
                    running = false;
                    std::cout << "  Stop"s << std::endl;
                } else {
                    std::cout << "  Message: "s << m << std::endl;
                }
            }
            break;
        }
    }
    return EXIT_SUCCESS;
}
