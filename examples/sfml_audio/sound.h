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

#pragma once

#include <math.h>

namespace sound {

#define TWOPI 6.283185307

short SineWave(double time, double freq, double amp)
{
    short result;
    double tpc = 44100 / freq; // ticks per cycle
    double cycles = time / tpc;
    double rad = TWOPI * cycles;
    short amplitude = 32767 * amp;
    result = amplitude * sin(rad);
    return result;
}

short SquareWave(double time, double freq, double amp)
{
    short result = 0;
    int tpc = 44100 / freq; // ticks per cycle
    int cyclepart = int(time) % tpc;
    int halfcycle = tpc / 2;
    short amplitude = 32767 * amp;
    if (cyclepart < halfcycle) {
        result = amplitude;
    }
    return result;
}

short Noise(double amp)
{
    short result = 0;
    short amplitude = 32767 * amp;
    result = rand() % amplitude;
    return result;
}
}
