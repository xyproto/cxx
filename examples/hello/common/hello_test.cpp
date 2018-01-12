#include "hello.h"
#include "test.h"

using namespace std::literals;

void hello_test() { equal(hello(), "Hello, World!"s); }

int main() {
    hello_test();
    return 0;
}
