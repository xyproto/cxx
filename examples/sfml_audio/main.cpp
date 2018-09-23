// From: https://github.com/pbohun/sound-gen/
/*
Copyright (c) 2015, pbohun
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this
  list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.

* Neither the name of fasm-tutorials nor the names of its
  contributors may be used to endorse or promote products derived from
  this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
*/

#include "sound.h"
#include <SFML/Audio.hpp>
#include <SFML/Graphics.hpp>
#include <vector>

using namespace std;

int main()
{
    sf::RenderWindow window(sf::VideoMode(256, 256), "Audio");

    sf::SoundBuffer buffer;
    vector<sf::Int16> samples;

    // https://www.seventhstring.com/resources/notefrequencies.html

    for (int i = 0; i < 44100 * 0.5; ++i) {
        samples.push_back(sound::SquareWave(i, 65.41, 0.9));
    }
    for (int i = 44100 * 0.5; i < 44100; ++i) {
        samples.push_back(sound::SquareWave(i, 77.78, 0.9));
    }
    for (int i = 44100; i < 44100 * 1.5; ++i) {
        samples.push_back(sound::SquareWave(i, 87.31, 0.9));
    }
    for (int i = 44100 * 1.5; i < 44100 * 2; ++i) {
        samples.push_back(sound::SquareWave(i, 130.8, 0.9));
    }

    buffer.loadFromSamples(&samples[0], samples.size(), 1, 44100);

    sf::Sound sound;
    sound.setBuffer(buffer);
    sound.play();

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
    }

    return 0;
}
