#include <cstdlib>
#include <iostream>
#include <string>

#include "fcgio.h"

using namespace std::string_literals;

auto main() -> int
{
    // Save the stdio streambufs
    auto cin_streambuf = std::cin.rdbuf();
    auto cout_streambuf = std::cout.rdbuf();
    auto cerr_streambuf = std::cerr.rdbuf();

    FCGX_Init();

    FCGX_Request request;
    FCGX_InitRequest(&request, 0, 0);

    while (FCGX_Accept_r(&request) == 0) {
        fcgi_streambuf cin_fcgi_streambuf(request.in);
        fcgi_streambuf cout_fcgi_streambuf(request.out);
        fcgi_streambuf cerr_fcgi_streambuf(request.err);

        std::cin.rdbuf(&cin_fcgi_streambuf);
        std::cout.rdbuf(&cout_fcgi_streambuf);
        std::cerr.rdbuf(&cerr_fcgi_streambuf);

        std::cout << "Content-type: text/html; charset=utf-8\r\n"s
                  << "\r\n"s
                  << "<!doctype html>\n"s
                  << "<html>\n"s
                  << "  <head>\n"s
                  << "    <title>FastCGI</title>\n"s
                  << "  </head>\n"s
                  << "  <body>\n"s
                  << "    <h1>FastCGI works</h1>\n"s
                  << "    <p>Here are some UTF-8 characters: æøå ÆØÅ</p>\n"s
                  << "  </body>\n"s
                  << "</html>\n"s;

        // The fcgi_streambuf destructor will flush automatically
    }

    // Restore the stdio streambufs
    std::cin.rdbuf(cin_streambuf);
    std::cout.rdbuf(cout_streambuf);
    std::cerr.rdbuf(cerr_streambuf);

    return EXIT_SUCCESS;
}
