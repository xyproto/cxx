#include <glib/gstdio.h>
#include <gtk/gtk.h>

static void print_hello(GtkWidget* widget, gpointer data)
{
    g_print("Hello World\n");
}

static void quit_cb(GtkWindow* window)
{
    gtk_window_close(window);
}

static void activate(GtkApplication* app, gpointer user_data)
{
    // Construct a GtkBuilder instance and load our UI description
    GtkBuilder* builder = gtk_builder_new();
    gtk_builder_add_from_file(builder, "main.ui", nullptr);

    // Connect signal handlers to the constructed widgets
    GObject* window = gtk_builder_get_object(builder, "window");
    gtk_window_set_application(GTK_WINDOW(window), app);

    GObject* button = gtk_builder_get_object(builder, "button1");
    g_signal_connect(button, "clicked", G_CALLBACK(print_hello), nullptr);

    button = gtk_builder_get_object(builder, "button2");
    g_signal_connect(button, "clicked", G_CALLBACK(print_hello), nullptr);

    button = gtk_builder_get_object(builder, "quit");
    g_signal_connect_swapped(button, "clicked", G_CALLBACK(quit_cb), window);

    gtk_widget_show(GTK_WIDGET(window));

    // The builder is not needed anymore
    g_object_unref(builder);
}

int main(int argc, char* argv[])
{
    GtkApplication* app = gtk_application_new("org.gtk.example", G_APPLICATION_FLAGS_NONE);
    g_signal_connect(app, "activate", G_CALLBACK(activate), nullptr);

    int status = g_application_run(G_APPLICATION(app), argc, argv);
    g_object_unref(app);

    return status;
}
