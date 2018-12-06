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

    return EXIT_SUCCESS;
}
