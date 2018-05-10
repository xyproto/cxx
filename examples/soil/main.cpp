#include "GL/gl.h"
#include "SOIL/SOIL.h"
#include <cstdio>

int main()
{

    /* load an image file directly as a new OpenGL texture */
    GLuint tex_2d = SOIL_load_OGL_texture("img.png", SOIL_LOAD_AUTO, SOIL_CREATE_NEW_ID,
        SOIL_FLAG_MIPMAPS | SOIL_FLAG_INVERT_Y | SOIL_FLAG_NTSC_SAFE_RGB
            | SOIL_FLAG_COMPRESS_TO_DXT);

    /* check for an error during the load process */
    if (0 == tex_2d) {
        printf("SOIL loading error: '%s'\n", SOIL_last_result());
    }

    return 0;
}
