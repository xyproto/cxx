#include <iostream>

// reactphysics3d
#include "mathematics/mathematics.h"

using namespace reactphysics3d;

int main()
{
    auto v3 = Vector3(1, 2, 3);
    std::cout << v3.length() << std::endl;
}
