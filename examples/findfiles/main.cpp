#include <filesystem>
#include <iostream>
#include <string>

using namespace std::string_literals;

auto main() -> int
{
    auto path = ".."s;
    for (auto& found : std::filesystem::directory_iterator(path)) {
        std::cout << found << std::endl;
    }
    return 0;
}
