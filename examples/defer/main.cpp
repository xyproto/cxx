// Example of similar functionality to "defer" in Go
// Thanks @pepper_chico: https://stackoverflow.com/a/33055669/131264

#include <cstdlib>
#include <iostream>
#include <memory>
#include <string>

using namespace std::string_literals;

int main(int argc, char** argv)
{
    std::cout << "Start of main function"s << std::endl;

    std::shared_ptr<void> defer1(
        nullptr, [](...) { std::cout << "DEFER 1: This should come last"s << std::endl; });

    std::shared_ptr<void> defer2(nullptr, [](...) {
        std::cout << "DEFER 2: This should come right before the last one"s << std::endl;
    });

    std::cout << "End of main function"s << std::endl;

    return EXIT_SUCCESS;
}
