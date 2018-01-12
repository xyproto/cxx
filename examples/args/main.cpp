#include <iostream>

int main(int argc, char** argv) {
    for (int i = 1; i < argc; ++i) {
        std::cout << "arg " << i << ": " << argv[i] << std::endl;
    }
    if (argc <= 1) {
        std::cout << "no arguments" << std::endl;
    }
}
