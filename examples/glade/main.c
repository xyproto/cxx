#include <gtk/gtk.h>

// on_winMain_destroy is called when the window is closed
void on_winMain_destroy()
{
    gtk_main_quit();
}

// on_btnOK_clicked is called when the button is clicked
void on_btnOK_clicked()
{
    gtk_main_quit();
}

int main(int argc, char* argv[])
{
    gtk_init(&argc, &argv);

    GtkBuilder* builder = gtk_builder_new();
    gtk_builder_add_from_file(builder, "main.glade", NULL);

    GtkWidget* window = GTK_WIDGET(gtk_builder_get_object(builder, "winMain"));
    gtk_builder_connect_signals(builder, NULL);

    g_object_unref(builder);

    gtk_widget_show(window);
    gtk_main();

    return 0;
}
