#include <giomm-2.4/giomm.h>

int main(int argc, char* argv[])
{
    auto Application = Gio::Application::create("custom.notification", Gio::APPLICATION_FLAGS_NONE);
    Application->register_application();

    auto Notification = Gio::Notification::create("What's cooking?");
    Notification->set_body("The stew is done.");

    auto Icon = Gio::ThemedIcon::create("dialog-information");
    Notification->set_icon(Icon);

    Application->send_notification(Notification);

    return 0;
}
