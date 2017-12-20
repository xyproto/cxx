#include "test.h"
#include "hello.h"

void hello_test() {
  equal(hello(), "Hello, World!"s);
}

int main() {
  hello_test();
  return 0;
}
