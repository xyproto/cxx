/* ----------------------------------------------------------------------------
   libconfig - A library for processing structured configuration files
   Copyright (C) 2005-2010  Mark A Lindner

   This file is part of libconfig.

   This library is free software; you can redistribute it and/or
   modify it under the terms of the GNU Lesser General Public License
   as published by the Free Software Foundation; either version 2.1 of
   the License, or (at your option) any later version.

   This library is distributed in the hope that it will be useful, but
   WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
   Lesser General Public License for more details.

   You should have received a copy of the GNU Library General Public
   License along with this library; if not, see
   <http://www.gnu.org/licenses/>.
   ----------------------------------------------------------------------------
*/

#include <iomanip>
#include <iostream>
#include <libconfig.h++>
#include <string>

using std::string;

// This example reads the configuration file 'example.cfg' and displays
// some of its contents.

int main()
{
    auto filename = "example.cfg";
    libconfig::Config cfg;

    // Read the file. If there is an error, report it and exit.
    try {
        cfg.readFile(filename);
    } catch (const libconfig::FileIOException& fioex) {
        std::cerr << "I/O error while reading " << filename << std::endl;
        return EXIT_FAILURE;
    } catch (const libconfig::ParseException& pex) {
        std::cerr << "Parse error at " << pex.getFile() << ":" << pex.getLine() << " - "
                  << pex.getError() << " in " << filename << std::endl;
        return EXIT_FAILURE;
    }

    // Get the store name.
    try {
        string name = cfg.lookup("name");
        std::cout << "Store name: " << name << std::endl << std::endl;
    } catch (const libconfig::SettingNotFoundException& nfex) {
        std::cerr << "No 'name' setting in configuration file." << std::endl;
    }

    const auto& root = cfg.getRoot();

    // Output a list of all books in the inventory.
    try {
        const auto& books = root["inventory"]["books"];

        std::cout << std::setw(30) << std::left << "TITLE"
                  << "  " << std::setw(30) << std::left << "AUTHOR"
                  << "   " << std::setw(6) << std::left << "PRICE"
                  << "  "
                  << "QTY" << std::endl;

        for (const auto& book : books) {
            // Only output the record if all of the expected fields are present.
            string title, author;
            double price;
            int qty;

            if (!(book.lookupValue("title", title) && book.lookupValue("author", author)
                    && book.lookupValue("price", price) && book.lookupValue("qty", qty)))
                continue;

            std::cout << std::setw(30) << std::left << title << "  " << std::setw(30) << std::left
                      << author << "  " << '$' << std::setw(6) << std::right << price << "  "
                      << qty << std::endl;
        }
        std::cout << std::endl;
    } catch (const libconfig::SettingNotFoundException& nfex) {
        // Ignore.
    }

    // Output a list of all books in the inventory.
    try {
        const auto& movies = root["inventory"]["movies"];

        std::cout << std::setw(30) << std::left << "TITLE"
                  << "  " << std::setw(10) << std::left << "MEDIA"
                  << "   " << std::setw(6) << std::left << "PRICE"
                  << "  "
                  << "QTY" << std::endl;

        for (const auto& movie : movies) {
            // Only output the record if all of the expected fields are present.
            string title, media;
            double price;
            int qty;

            if (!(movie.lookupValue("title", title) && movie.lookupValue("media", media)
                    && movie.lookupValue("price", price) && movie.lookupValue("qty", qty)))
                continue;

            std::cout << std::setw(30) << std::left << title << "  " << std::setw(10) << std::left
                      << media << "  " << '$' << std::setw(6) << std::right << price << "  " << qty
                      << std::endl;
        }
        std::cout << std::endl;
    } catch (const libconfig::SettingNotFoundException& nfex) {
        // Ignore.
    }

    return EXIT_SUCCESS;
}
