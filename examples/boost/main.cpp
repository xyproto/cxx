#include <boost/filesystem.hpp>
#include <iostream>

using namespace boost::filesystem;
using namespace std::string_literals;

int main(int argc, char** argv)
{
    std::cout << "Size of this executable: "s << file_size(argv[0]) << " bytes"s << std::endl;
    return 0;
}
