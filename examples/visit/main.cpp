// https://www.cppstories.com/2018/09/visit-variants/

#include <iostream>
#include <variant>

struct Fluid { };
struct LightItem { };
struct HeavyItem { };
struct FragileItem { };

template<class... Ts> struct overload : Ts... { using Ts::operator()...; };

int main() {
    std::variant<Fluid, LightItem, HeavyItem, FragileItem> package;

    // will output "fluid"
    std::visit(overload{
        [](Fluid& )       { std::cout << "fluid\n"; },
        [](LightItem& )   { std::cout << "light item\n"; },
        [](HeavyItem& )   { std::cout << "heavy item\n"; },
        [](FragileItem& ) { std::cout << "fragile\n"; }
    }, package);
}
