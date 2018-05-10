#include <SFML/Graphics.hpp>

int main()
{
    sf::RenderWindow window(sf::VideoMode(256, 256), "Hello, SFML!");
    sf::CircleShape shape(128.f);
    shape.setFillColor(sf::Color::Green);

    while (window.isOpen()) {
        sf::Event event;
        while (window.pollEvent(event)) {
            if (event.type == sf::Event::Closed) {
                window.close();
            }
        }
        if (sf::Keyboard::isKeyPressed(sf::Keyboard::Escape)
            || sf::Keyboard::isKeyPressed(sf::Keyboard::Q)) {
            window.close();
        }

        window.clear();
        window.draw(shape);
        window.display();
    }

    return 0;
}
