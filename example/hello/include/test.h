#pragma once

#include <iostream>
#include <cstdlib>

using std::cout;
using std::endl;
using namespace std::literals;

template<typename T>
void equal(T a, T b) {
    if (a == b) {
        cout << "YES" << endl;
    } else {
        cout << "NO" << endl;
        exit(EXIT_FAILURE);
    }
}
