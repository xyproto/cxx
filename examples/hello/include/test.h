#pragma once

#include <cstdlib>
#include <iostream>

template <typename T> void equal(T a, T b)
{
    if (a == b) {
        std::cout << "YES" << std::endl;
    } else {
        std::cerr << "NO" << std::endl;
        exit(EXIT_FAILURE);
    }
}
