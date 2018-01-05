#include <iostream>
#include <string>

using namespace std::literals;

#if defined(__amigaos__)
const std::string os = "Hello, Amiga!"s;
#elif defined(__APPLE__)
const std::string os = "Hello, macOS!"s;
#elif defined(__linux)
const std::string os = "Hello, Linux!"s;
#elif defined(__gnu_linux__)
const std::string os = "Hello, GNU/Linux!"s;
#elif defined(__gnuhurd__)
const std::string os = "Hello, GNU/Hurd!"s;
#elif defined(__FreeBSD__)
const std::string os = "Hello, FreeBSD!"s;
#elif defined(__NetBSD__)
const std::string os = "Hello, NetBSD!"s;
#elif defined(__OpenBSD__)
const std::string os = "Hello, OpenBSD!"s;
#elif defined(__DragonFly__)
const std::string os = "Hello, DragonFly!"s;
#elif defined(__minix)
const std::string os = "Hello, Minix!"s;
#elif defined(FREEDOS)
const std::string os = "Hello, FreeDOS!"s;
#elif defined(__MSDOS__)
const std::string os = "Hello, MS-DOS!"s;
#elif defined(__DOS__)
const std::string os = "Hello, DOS!"s;
#elif defined(__HAIKU__)
const std::string os = "Hello, Haiku!"s;
#elif defined(__BEOS__)
const std::string os = "Hello, BeOS!"s;
#elif defined(__unix__)
const std::string os = "Hello, UNIX!"s;
#elif defined(PLAN9)
const std::string os = "Hello, Plan9!"s;
#else
const std::string os = "Hello, Other operating system!"s;
#endif

auto main() -> int {
  std::cout << os << std::endl;
  return 0;
}
