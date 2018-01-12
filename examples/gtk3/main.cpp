#include <gdk/gdkkeysyms.h>
#include <gtk/gtk.h>

static gboolean check_escape(GtkWidget* widget, GdkEventKey* event,
                             gpointer data) {
    if (event->keyval == GDK_KEY_Escape || event->keyval == GDK_KEY_q) {
        g_application_quit(G_APPLICATION(data));
        return true;
    }
    return false;
}

static void activate(GtkApplication* app, gpointer user_data) {
    auto window = gtk_application_window_new(app);
    gtk_window_set_title(GTK_WINDOW(window), "Hello, World!");
    gtk_window_set_default_size(GTK_WINDOW(window), 320, 200);
    gtk_widget_show_all(window);
    g_signal_connect(window, "key_press_event", G_CALLBACK(check_escape), app);
}

int main(int argc, char** argv) {
    auto app = gtk_application_new("org.gtk.example", G_APPLICATION_FLAGS_NONE);
    g_signal_connect(app, "activate", G_CALLBACK(activate), nullptr);
    auto status = g_application_run(G_APPLICATION(app), argc, argv);
    g_object_unref(app);
    return status;
}
