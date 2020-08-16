#include <cstdlib>
#include <iostream>
#include <string>

using namespace std::string_literals;

int main(int argc, char** argv)
{
    // Using the template syntax for generic lambdas that were introduced in C++20.
    auto twice = []<typename T>(T x) { return x + x; };

    // twice can double anything that can be doubled
    std::cout << twice("SNU"s) << " " << twice(21) << std::endl;

    // output (1, 2, 3)
    int x = 0, y = 0, z = 0;
    [&]() noexcept { ++x; ++++y; ++++++z; }();
    std::cout << "(" << x << ", " << y << ", " << z << ")" << std::endl;

    return EXIT_SUCCESS;
}
