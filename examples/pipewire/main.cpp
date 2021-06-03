#include <iostream>
#include <string>

// Including this path instead of just pipewire/pipewire.h lets cxx find the versioned include directory
#include <pipewire-0.3/pipewire/pipewire.h>

using namespace std::string_literals;

// Based on https://docs.pipewire.org/page_tutorial2.html for version 0.3.29 of PipeWire

static void registry_event_global(
    void* data,
    uint32_t id,
    uint32_t permissions,
    const char* type,
    uint32_t version,
    const struct spa_dict* props)
{
    std::cout << "object id:"s << id << " type:"s << type << "/"s << version << std::endl;
}

static const struct pw_registry_events registry_events = {
    PW_VERSION_REGISTRY_EVENTS,
    registry_event_global,
};

int main(int argc, char* argv[])
{
    pw_init(&argc, &argv);

    std::cout << "Compiled with libpipewire "s << pw_get_headers_version() << std::endl;
    std::cout << "Linked with libpipewire "s << pw_get_library_version() << std::endl;

    auto loop = pw_main_loop_new(nullptr);
    auto ctx = pw_context_new(pw_main_loop_get_loop(loop), nullptr, 0);
    auto core = pw_context_connect(ctx, nullptr, 0);
    auto registry = pw_core_get_registry(core, PW_VERSION_REGISTRY, 0);

    struct spa_hook registry_listener;
    spa_zero(registry_listener);
    pw_registry_add_listener(registry, &registry_listener, &registry_events, nullptr);

    pw_main_loop_run(loop);

    pw_proxy_destroy((struct pw_proxy*)registry);
    pw_core_disconnect(core);
    pw_context_destroy(ctx);
    pw_main_loop_destroy(loop);

    return EXIT_SUCCESS;
}
