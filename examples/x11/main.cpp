#include "x.h"

#include <chrono>
#include <csignal>
#include <iostream>
#include <memory>
#include <thread>

using namespace std::string_literals;
using namespace X;

volatile sig_atomic_t running = true;

void stop(int x)
{
    running = false;
    std::cout << std::endl;
}

auto main(int argc, char** argv) -> int
{
    std::unique_ptr<X::Window> win;
    try {
        win = std::make_unique<X::Window>(10, 10, 100, 100);
    } catch (const std::runtime_error& err) {
        std::cerr << "ERROR: " << err.what() << std::endl;
        return EXIT_FAILURE;
    }

    win->SelectInput();
    win->MapWindow();

    XEvent e;

    signal(SIGINT, stop);

    while (running) {
        // This check exists so that event-checking can be non-blocking if the program is
        // interrupted by SIGINT
        if (XPending(win->GetDisplay()) == 0) {
            std::this_thread::sleep_for(std::chrono::milliseconds(50));
            continue;
        }
        XNextEvent(win->GetDisplay(), &e);
        switch (e.type) {
        case Expose:
            win->FillRectangle(10, 10, 20, 20);
            win->DrawString(10, 50, "Hello, World!"s);
            break;
        case KeyPress:
            // TODO: Check for either Esc or "q"
            std::cout << "KEYPRESS" << std::endl;
            running = false;
            break;
        case ButtonPress:
            switch (e.xbutton.button) {
            case 1:
                std::cout << "Left Click" << std::endl;
                auto x = e.xbutton.x;
                auto y = e.xbutton.y;
                win->FillRectangle(x, y, 20, 20);
                break;
            }
            break;
        case ClientMessage:
            std::cout << "CLIENT MESSAGES" << std::endl;
            for (const unsigned long& m : e.xclient.data.l) {
                if (win->WindowCloseMessage(m)) {
                    running = false;
                    std::cout << "STOP" << std::endl;
                } else {
                    std::cout << "MESSAGE " << m << std::endl;
                }
            }
            break;
        }
    }
    return EXIT_SUCCESS;
}
