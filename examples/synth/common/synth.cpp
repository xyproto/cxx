// Based on unlicensed sample code by Harry Lundstrom
// https://github.com/lundstroem/synth-samples-sdl2

#include "synth.h"

static Sint32 last_key = 0;

// SDL
static uint16_t buffer_size = 4096; // must be a power of two, decrease to allow for a lower
                                    // latency, increase to reduce risk of underrun.

static SDL_AudioSpec audio_spec;
static SDL_Window* window = nullptr;

static int sample_rate = 44100;
const int table_length = 1024;
static bool key_pressed = false;
static int last_note = 0;

// voice
static double phase_double = 0;
static int phase_int = 0;
static int16_t* sine_wave_table;
static int note = -1; // integer representing halfnotes.
static int octave = 2;
static int max_note = 131;
static int min_note = 12;

static double envelope_cursor = 0;
static double envelope_speed_scale = 1; // set envelope speed 1-8
static double envelope_increment_base
    = 0; // this will be set in init_data based on current samplingrate.

// amplitude smoothing
static double current_amp = 0;
static double target_amp = 0;
static double smoothing_amp_speed = 0.01;
static double smoothing_enabled = true;

using namespace std::string_literals;

void build_sine_table(int16_t* data, int wave_length)
{
    /*
        Build sine table to use as oscillator:
        Generate a 16bit signed integer sinewave table with 1024 samples.
        This table will be used to produce the notes.
        Different notes will be created by stepping through
        the table at different intervals (phase).
    */
    double phase_increment = (2.0f * pi) / (double)wave_length;
    double current_phase = 0;
    for (int i = 0; i < wave_length; i++) {
        int sample = (int)(sin(current_phase) * INT16_MAX);
        data[i] = (int16_t)sample;
        current_phase += phase_increment;
    }
}

/*
 * This function is called whenever the audio buffer needs to be filled to allow
 * for a continuous stream of audio.
 * Write samples to byteStream according to byteStreamLength.
 * The audio buffer is interleaved, meaning that both left and right channels exist in the
 * same buffer.
 */
void audio_callback(void* unused, Uint8* byte_stream, int byte_stream_length)
{
    // zero the buffer
    memset(byte_stream, 0, byte_stream_length);

    if (quit_audio) {
        return;
    }

    // cast buffer as 16bit signed int.
    Sint16* s_byte_stream = (Sint16*)byte_stream;

    // buffer is interleaved, so get the length of 1 channel.
    int remain = byte_stream_length / 2;

    // split the rendering up in chunks to make it buffersize agnostic.
    long chunk_size = 64;
    int iterations = remain / chunk_size;
    for (long i = 0; i < iterations; i++) {
        long begin = i * chunk_size;
        long end = (i * chunk_size) + chunk_size;
        write_samples(s_byte_stream, begin, end, chunk_size);
    }
}

void write_samples(int16_t* s_byteStream, long begin, long end, long length)
{
    if (note > 0) {
        double d_sample_rate = sample_rate;
        double d_table_length = table_length;
        double d_note = note;

        // get correct phase increment for note depending on sample rate and table length.
        double phase_increment = (get_pitch(d_note) / d_sample_rate) * d_table_length;

        // loop through the buffer and write samples.
        for (int i = 0; i < length; i += 2) {
            phase_double += phase_increment;
            phase_int = (int)phase_double;
            if (phase_double >= table_length) {
                double diff = phase_double - table_length;
                phase_double = diff;
                phase_int = (int)diff;
            }

            if (phase_int < table_length && phase_int > -1) {
                if (s_byteStream != nullptr) {
                    int16_t sample = sine_wave_table[phase_int];
                    target_amp = update_envelope();
                    if (smoothing_enabled) {
                        // move current amp towards target amp for a smoother transition.
                        if (current_amp < target_amp) {
                            current_amp += smoothing_amp_speed;
                            if (current_amp > target_amp) {
                                current_amp = target_amp;
                            }
                        } else if (current_amp > target_amp) {
                            current_amp -= smoothing_amp_speed;
                            if (current_amp < target_amp) {
                                current_amp = target_amp;
                            }
                        }
                    } else {
                        current_amp = target_amp;
                    }
                    sample *= current_amp; // scale volume.
                    s_byteStream[i + begin] = sample; // left channel
                    s_byteStream[i + begin + 1] = sample; // right channel
                }
            }
        }
    }
}

void cleanup_data(void)
{
    free_memory(sine_wave_table);
    std::cout << "alloc count:" << alloc_count << std::endl;
}

void setup_sdl(void)
{
    // Get current display mode of all displays.
    SDL_DisplayMode current;
    for (int i = 0; i < SDL_GetNumVideoDisplays(); ++i) {
        int should_be_zero = SDL_GetCurrentDisplayMode(i, &current);
        if (should_be_zero != 0) {
            // In case of error...
            SDL_Log("Could not get display mode for video display #%d: %s", i, SDL_GetError());
        } else {
            // On success, print the current display mode.
            SDL_Log("Display #%d: current display mode is %dx%dpx @ %dhz. \n", i, current.w,
                current.h, current.refresh_rate);
        }
    }

    window = SDL_CreateWindow("synth_samples_sdl2_3", SDL_WINDOWPOS_CENTERED,
        SDL_WINDOWPOS_CENTERED, 640, 480, SDL_WINDOW_OPENGL);
    if (window == nullptr) {
        printf("Failed to create window:%s", SDL_GetError());
    }
}

int setup_sdl_audio(void)
{

    SDL_Init(SDL_INIT_AUDIO | SDL_INIT_TIMER);
    SDL_AudioSpec want;
    SDL_zero(want);
    SDL_zero(audio_spec);

    want.freq = sample_rate;
    // request 16bit signed little-endian sample format.
    want.format = AUDIO_S16LSB;
    // request 2 channels (stereo)
    want.channels = 2;
    want.samples = buffer_size;

    /*
        Tell SDL to call this function (audio_callback) that we have defined whenever there is an
       audiobuffer ready to be filled.
    */
    want.callback = audio_callback;

    printf("\naudioSpec want\n");
    printf("----------------\n");
    printf("sample rate:%d\n", want.freq);
    printf("channels:%d\n", want.channels);
    printf("samples:%d\n", want.samples);
    printf("----------------\n\n");

    audio_device = SDL_OpenAudioDevice(nullptr, 0, &want, &audio_spec, 0);

    printf("\naudioSpec get\n");
    printf("----------------\n");
    printf("sample rate:%d\n", audio_spec.freq);
    printf("channels:%d\n", audio_spec.channels);
    printf("samples:%d\n", audio_spec.samples);
    printf("size:%d\n", audio_spec.size);
    printf("----------------\n");

    if (audio_device == 0) {
        printf("\nFailed to open audio: %s\n", SDL_GetError());
        return 1;
    }

    if (audio_spec.format != want.format) {
        printf("\nCouldn't get requested audio format.\n");
        return 2;
    }

    buffer_size = audio_spec.samples;
    SDL_PauseAudioDevice(audio_device, 0); // unpause audio.
    return 0;
}

// returns true when it's time to quit
bool check_sdl_events(SDL_Event e)
{
    while (SDL_PollEvent(&e)) {
        switch (e.type) {
        case SDL_QUIT:
            return true;
        case SDL_KEYDOWN:
            if (handle_key_down(&e.key.keysym)) {
                return true;
            }
            break;
        case SDL_KEYUP:
            if (handle_key_up(&e.key.keysym)) {
                return true;
            }
            break;
        }
    }
    return false;
}

void destroy_sdl(void) { SDL_DestroyWindow(window); }

void init_data(void)
{
    // allocate memory for sine table and build it.
    sine_wave_table = (int16_t*)alloc_memory(sizeof(int16_t) * table_length, "PCM table");
    build_sine_table(sine_wave_table, table_length);

    // set envelope increment size based on samplerate.
    envelope_increment_base = 1 / (double)(sample_rate / 2);
}

bool handle_key_up(SDL_Keysym* keysym)
{
    switch (keysym->sym) {
    case SDLK_PLUS:
        break;
    case SDLK_MINUS:
        break;
    default:
        // if the last notekey pressed is released
        if (last_key == keysym->sym) {
            key_pressed = false;
            last_note = -1;
        }
        break;
    }
    return false;
}

bool handle_key_down(SDL_Keysym* keysym)
{
    switch (keysym->sym) {
    case SDLK_PLUS:
        if (octave < 5) {
            octave++;
            printf("increased octave to:%d\n", octave);
        }
        break;
    case SDLK_MINUS:
        if (octave > 0) {
            octave--;
            printf("decreased octave to:%d\n", octave);
        }
        break;
    case SDLK_ESCAPE:
    case SDLK_q:
        return true;
    default:
        last_key = keysym->sym;
        handle_note_keys(keysym);
        key_pressed = true;
        break;
    }
    return false;
}

double update_envelope(void)
{

    // advance envelope cursor and return the target amplitude value.

    double amp = 0;
    if (key_pressed && envelope_cursor < 3 && envelope_cursor > 2) {
        // if a note key is longpressed and cursor is in range, stay for sustain.
        amp = get_envelope_amp_by_node(2, envelope_cursor);
    } else {
        double speed_multiplier = pow(2, envelope_speed_scale);
        double cursor_inc = envelope_increment_base * speed_multiplier;
        envelope_cursor += cursor_inc;
        if (envelope_cursor < 1) {
            amp = get_envelope_amp_by_node(0, envelope_cursor);
        } else if (envelope_cursor < 2) {
            amp = get_envelope_amp_by_node(1, envelope_cursor);
        } else if (envelope_cursor < 3) {
            amp = get_envelope_amp_by_node(2, envelope_cursor);
        } else {
            amp = envelope_data[3];
        }
    }
    return amp;
}

void handle_note_keys(SDL_Keysym* keysym)
{

    // change note depending on which key is pressed.

    int new_note = note;
    switch (keysym->sym) {
    case SDLK_z:
        new_note = 12;
        break;
    case SDLK_s:
        new_note = 13;
        break;
    case SDLK_x:
        new_note = 14;
        break;
    case SDLK_d:
        new_note = 15;
        break;
    case SDLK_c:
        new_note = 16;
        break;
    case SDLK_v:
        new_note = 17;
        break;
    case SDLK_g:
        new_note = 18;
        break;
    case SDLK_b:
        new_note = 19;
        break;
    case SDLK_h:
        new_note = 20;
        break;
    case SDLK_n:
        new_note = 21;
        break;
    case SDLK_j:
        new_note = 22;
        break;
    case SDLK_m:
        new_note = 23;
        break;
    case SDLK_COMMA:
        new_note = 24;
        break;
    case SDLK_l:
        new_note = 25;
        break;
    case SDLK_PERIOD:
        new_note = 26;
        break;

    // upper keyboard
    case SDLK_2:
        new_note = 25;
        break;
    case SDLK_w:
        new_note = 26;
        break;
    case SDLK_3:
        new_note = 27;
        break;
    case SDLK_e:
        new_note = 28;
        break;
    case SDLK_r:
        new_note = 29;
        break;
    case SDLK_5:
        new_note = 30;
        break;
    case SDLK_t:
        new_note = 31;
        break;
    case SDLK_6:
        new_note = 32;
        break;
    case SDLK_y:
        new_note = 33;
        break;
    case SDLK_7:
        new_note = 34;
        break;
    case SDLK_u:
        new_note = 35;
        break;
    case SDLK_i:
        new_note = 36;
        break;
    case SDLK_9:
        new_note = 37;
        break;
    case SDLK_o:
        new_note = 38;
        break;
    case SDLK_0:
        new_note = 39;
        break;
    case SDLK_p:
        new_note = 40;
        break;
    default:
        return;
        break;
    }

    if (new_note > -1) {

        note = new_note;
        note += (octave * 12);
        if (note > max_note) {
            note = max_note;
        }
        if (note < min_note) {
            note = min_note;
        }

        // if note is the same as last note, it's still held on sustain. Only set a new note if it
        // differs from the last one.

        if (note != last_note) {
            print_note(note);
            last_note = note;

            // reset envelope cursor
            envelope_cursor = 0;
        }
    }
}

void print_note(int n)
{
    int note_without_octave = n % 12;
    int note_octave = (n / 12) - 1;
    std::string note_chars;
    switch (note_without_octave) {
    case 0:
        note_chars = "C-"s;
        break;
    case 1:
        note_chars = "C#"s;
        break;
    case 2:
        note_chars = "D-"s;
        break;
    case 3:
        note_chars = "D#"s;
        break;
    case 4:
        note_chars = "E-"s;
        break;
    case 5:
        note_chars = "F-"s;
        break;
    case 6:
        note_chars = "F#"s;
        break;
    case 7:
        note_chars = "G-"s;
        break;
    case 8:
        note_chars = "G#"s;
        break;
    case 9:
        note_chars = "A-"s;
        break;
    case 10:
        note_chars = "A#"s;
        break;
    case 11:
        note_chars = "B-"s;
        break;
    }
    printf("note: %s%d pitch: %fHz\n", note_chars.c_str(), note_octave, get_pitch(n));
}
