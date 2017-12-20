#include "test.h"
#include "hello.h"

using namespace std::literals;

void hello_test() {
  equal(hello(), "Hello, World!"s);
}

int main() {
  hello_test();
  return 0;
}
