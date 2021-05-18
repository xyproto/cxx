#include <concepts>
#include <functional>
#include <iostream>

template <typename F>
requires std::invocable<F&, int> void PrintSquare(const std::vector<int>& vec, F fn)
{
    for (auto& elem : vec)
        std::cout << fn(elem) << '\n';
}

auto main() -> int
{
    std::vector ints { 1, 2, 3, 4, 5 };
    PrintSquare(ints, [](int x) { return x * x; });
}
