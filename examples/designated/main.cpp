#include <cstdlib>
#include <iomanip>
#include <iostream>
#include <ostream>
#include <string>

using namespace std::string_literals;

class Point {
public:
    double x;
    double y;
    double z;
    std::string str();
};

std::ostream& operator<<(std::ostream& output, const Point& p)
{
    using std::setfill;
    using std::setw;
    output << "{ "s << setfill(' ') << setw(3) << p.x << ", "s << setfill(' ') << setw(3) << p.y
           << ", "s << setfill(' ') << setw(3) << p.z << " }"s;
    return output;
}

Point operator+(const Point& a, const Point& b)
{
    return Point { .x = a.x + b.x, .y = a.y + b.y, .z = a.z + b.z };
}

Point operator*(const Point& a, const Point& b)
{
    return Point { .x = a.x * b.x, .y = a.y * b.y, .z = a.z * b.z };
}

int main(int argc, char** argv)
{
    // designated initializers
    Point p1 { .x = 1, .y = 2, .z = 3 };
    Point p2 { .y = 42 };

    using std::cout;
    using std::endl;

    cout << "     p1 = " << p1 << endl;
    cout << "     p2 = " << p2 << endl;
    cout << "p1 + p2 = " << p1 + p2 << endl;
    cout << "p1 * p2 = " << p1 * p2 << endl;

    return EXIT_SUCCESS;
}
