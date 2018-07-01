// Based on: https://stackoverflow.com/a/5469561/131264

#include <chrono>
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <iostream>
#include <thread>

#ifdef __APPLE__
#include <OpenAL.h>
#else
#include <AL/al.h>
#include <AL/alc.h>
#endif

#define CASE_RETURN(err)                                                                          \
    case (err):                                                                                   \
        return "##err"
const char* al_err_str(ALenum err)
{
    switch (err) {
        CASE_RETURN(AL_NO_ERROR);
        CASE_RETURN(AL_INVALID_NAME);
        CASE_RETURN(AL_INVALID_ENUM);
        CASE_RETURN(AL_INVALID_VALUE);
        CASE_RETURN(AL_INVALID_OPERATION);
        CASE_RETURN(AL_OUT_OF_MEMORY);
    }
    return "unknown";
}
#undef CASE_RETURN

#define __al_check_error(file, line)                                                              \
    do {                                                                                          \
        ALenum err = alGetError();                                                                \
        for (; err != AL_NO_ERROR; err = alGetError()) {                                          \
            std::cerr << "AL Error " << al_err_str(err) << " at " << file << ":" << line          \
                      << std::endl;                                                               \
        }                                                                                         \
    } while (0)

#define al_check_error() __al_check_error(__FILE__, __LINE__)

void init_al()
{
    const char* defname = alcGetString(nullptr, ALC_DEFAULT_DEVICE_SPECIFIER);
    std::cout << "Default device: " << defname << std::endl;
    auto dev = alcOpenDevice(defname);
    auto ctx = alcCreateContext(dev, nullptr);
    alcMakeContextCurrent(ctx);
}

void exit_al()
{
    auto ctx = alcGetCurrentContext();
    auto dev = alcGetContextsDevice(ctx);
    alcMakeContextCurrent(nullptr);
    alcDestroyContext(ctx);
    alcCloseDevice(dev);
}

int main()
{
    /* initialize OpenAL */
    init_al();

    /* Create buffer to store samples */
    ALuint buf;
    alGenBuffers(1, &buf);
    al_check_error();

    /* Fill buffer with Sine-Wave */
    auto freq = 440.f;
    auto seconds = 4;
    unsigned int sample_rate = 22050;
    size_t buf_size = seconds * sample_rate;

    auto samples = new short[buf_size];
    for (size_t i = 0; i < buf_size; ++i) {
        samples[i] = 32760 * sin((2.f * float(M_PI) * freq) / sample_rate * i);
    }

    /* Download buffer to OpenAL */
    alBufferData(buf, AL_FORMAT_MONO16, samples, buf_size, sample_rate);
    al_check_error();

    /* Set-up sound source and play buffer */
    ALuint src = 0;
    alGenSources(1, &src);
    alSourcei(src, AL_BUFFER, buf);
    alSourcePlay(src);

    /* While sound is playing, sleep */
    al_check_error();
    std::this_thread::sleep_for(std::chrono::seconds(seconds));

    /* Deallocate OpenAL */
    exit_al();
    al_check_error();

    return 0;
}
