#include <iostream>
#include <string>

using namespace std::string_literals;

int main()
{
    std::string s = "but I have heard it works even if you don't believe in it";

    // In C++17, this is no longer undefined behavior
    std::cout
        << s.replace(0, 4, "").replace(s.find("even"), 4, "only").replace(s.find(" don't"), 6, "")
        << std::endl;

    // The example is from https://stackoverflow.com/a/38501596/131264
}
