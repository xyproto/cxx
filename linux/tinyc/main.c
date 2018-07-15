#include <unistd.h>

const void println(const char* s) {
	size_t len = 0;
	while (s[len++] != '\0');
	write(STDOUT_FILENO, s, len);
	static const char nl = '\n';
	write(STDOUT_FILENO, &nl, 1);
	fsync(STDOUT_FILENO);
}

int main() {
  	println("Hello, World!");
	return 0;
}
