#pragma once

#include <SDL2/SDL.h>
#include <iostream>
#include <string>

constexpr double pi = 3.14159265358979323846;
constexpr double chromatic_ratio = 1.059463094359295264562;

// general
static int alloc_count = 0;
static bool quit_audio = false;

static SDL_AudioDeviceID audio_device;
static double envelope_data[4] = { 1.0, 0.5, 0.5, 0.0 }; // ADSR amp range 0.0-1.0

// functions
void build_sine_table(int16_t* data, int wave_length);
void write_samples(int16_t* s_byteStream, long begin, long end, long length);
void cleanup_data(void);
void setup_sdl(void);
int setup_sdl_audio(void);
bool check_sdl_events(SDL_Event event);
void destroy_sdl(void);
void init_data(void);

bool handle_key_up(SDL_Keysym* keysym);
bool handle_key_down(SDL_Keysym* keysym);
void main_loop(void);
void handle_note_keys(SDL_Keysym* keysym);
void print_note(int n);

// amplitude envelope
double update_envelope(void);

// Calculate pitch from note value. Offset note by 57 halfnotes to get
// correct pitch from the range we have chosen for the notes.
inline double get_pitch(double n) { return pow(chromatic_ratio, n - 57) * 440; }

inline double get_envelope_amp_by_node(const int base_node, const double cursor)
{
    // interpolate amp value for the current cursor position.

    double n1 = base_node;
    double n2 = base_node + 1;
    double relative_cursor_pos = (cursor - n1) / (n2 - n1);
    double amp_diff = (envelope_data[base_node + 1] - envelope_data[base_node]);
    double amp = envelope_data[base_node] + (relative_cursor_pos * amp_diff);
    return amp;
}

inline void* alloc_memory(size_t size, const std::string& name)
{
    if (void* ptr = malloc(size); ptr != nullptr) {
        alloc_count++;
        return ptr;
    }
    std::cout << "alloc_memory error: malloc with size " << size
              << " returned nullptr.\n name:" << name << std::endl;
    return nullptr;
}

inline void* free_memory(void* ptr)
{
    if (ptr != nullptr) {
        free(ptr);
        alloc_count--;
    }
    return nullptr;
}
