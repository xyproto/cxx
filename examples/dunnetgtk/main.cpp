#include <cstdio>
#include <filesystem>
#include <iostream>
#include <string>
#include <vte/vte.h>

/*
 * A terminal emulator only for playing Dunnet.
 * Inspired by: https://vincent.bernat.ch/en/blog/2017-write-own-terminal
 */

using namespace std::string_literals;

// new_window creates and returns a Gtk window.
// The given title is used as the window title.
auto new_window(std::string const& title)
{
    auto window = gtk_window_new(GTK_WINDOW_TOPLEVEL);
    gtk_window_set_title(GTK_WINDOW(window), title.c_str());
    return window;
}

// new_color parses the given string and returns a GdkRGBA struct
// which must be freed after use.
auto new_color(std::string const& c)
{
    auto colorstruct = (GdkRGBA*)malloc(sizeof(GdkRGBA));
    gdk_rgba_parse(colorstruct, c.c_str());
    return colorstruct;
}

void eof() { std::cout << "bye" << std::endl; }

int main(int argc, char* argv[])
{
    // Initialize Gtk, the window and the terminal
    gtk_init(&argc, &argv);
    auto window = new_window("Dunnet"s);
    auto terminal = vte_terminal_new();

    // Build an array of strings, which is the command to be run
    const char* command[5];
    command[0] = "/usr/bin/emacs";
    command[1] = "-batch";
    command[2] = "-l";
    command[3] = "dunnet";
    command[4] = nullptr;

    using std::filesystem::exists;
    using std::filesystem::perms;
    using std::filesystem::status;

    // Check if the executable exists
    if (!exists(command[0])) {
        std::cerr << command[0] << " does not exist" << std::endl;
        return EXIT_FAILURE;
    }

    // Check if the executable is executable
    const auto perm = status(command[0]).permissions();
    if ((perm & perms::owner_exec) == perms::none) {
        std::cerr << command[0] << " is not executable for this user" << std::endl;
        return EXIT_FAILURE;
    }

    // Spawn a terminal
#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wdeprecated-declarations"
    vte_terminal_spawn_sync(VTE_TERMINAL(terminal), VTE_PTY_DEFAULT,
        nullptr, // working directory
        (char**)command, // command
        nullptr, // environment
        (GSpawnFlags)0, // spawn flags
        nullptr, nullptr, // child setup
        nullptr, // child PID
        nullptr, nullptr);
#pragma GCC diagnostic pop

    // Set background color to 95% opaque black
    auto black = new_color("rgba(0, 0, 0, 0.95)"s);
    vte_terminal_set_color_background(VTE_TERMINAL(terminal), black);
    free(black);

    // Set foreground color
    auto green = new_color("chartreuse"s);
    vte_terminal_set_color_foreground(VTE_TERMINAL(terminal), green);
    free(green);

    // Set font
    auto font_desc = pango_font_description_from_string("courier bold 16");
    vte_terminal_set_font(VTE_TERMINAL(terminal), font_desc);

    // Set cursor shape to UNDERLINE
    vte_terminal_set_cursor_shape(VTE_TERMINAL(terminal), VTE_CURSOR_SHAPE_UNDERLINE);

    // Set cursor blink to OFF
    vte_terminal_set_cursor_blink_mode(VTE_TERMINAL(terminal), VTE_CURSOR_BLINK_OFF);

    // Connect some signals
    g_signal_connect(window, "delete-event", gtk_main_quit, nullptr);
    g_signal_connect(terminal, "child-exited", gtk_main_quit, nullptr);
    g_signal_connect(terminal, "eof", eof, nullptr);

    // Add the terminal to the window
    gtk_container_add(GTK_CONTAINER(window), terminal);

    // Show the window and run the Gtk event loop
    gtk_widget_show_all(window);
    gtk_main();

    return EXIT_SUCCESS;
}
