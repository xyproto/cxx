// Based on https://github.com/hikiko/gl4
// Unknown license: https://github.com/hikiko/gl4/issues/1

#include <cassert>
#include <cmath>
#include <cstddef>
#include <cstdio>
#include <cstdlib>
#include <cstring>

#define GL_GLEXT_PROTOTYPES

#include <GL/freeglut.h>
#include <GL/glext.h>
#include <GL/glx.h>

#define M(i, j) (((i) << 2) + (j))
#define SPIRV

enum {
    UBLOCK_MATRIX,
};

enum { VATTR_VERTEX, VATTR_NORMAL, VATTR_TEXCOORD };

struct vertex {
    float x, y, z;
    float nx, ny, nz;
    float tu, tv;
};

struct mesh {
    struct vertex* varr;
    unsigned int* iarr;
    int vcount, icount;

    unsigned int vbo, ibo, vao;
};

struct matrix_state {
    float view_mat[16];
    float proj_mat[16];
    float mvmat[16];
    float mvpmat[16];
    float lpos[3];
}; // __attribute__((packed));

// Globals

struct mesh torus;
struct matrix_state matrix_state;

unsigned int g_tex;
unsigned int g_sdr;
unsigned int ubo_matrix;

static PFNGLSPECIALIZESHADERPROC gl_specialize_shader;

float cam_theta, cam_phi = 25, cam_dist = 4;
int prev_x, prev_y, bnstate[8];

// Forward declarations

void draw_mesh(struct mesh* mesh);
int link_program(unsigned int prog);
void GLAPIENTRY gldebug(GLenum src, GLenum type, GLuint id, GLenum severity, GLsizei len,
    const char* msg, const void* cls);

// Functions

void mat_identity(float* mat)
{
    memset(mat, 0, 16 * sizeof *mat);
    mat[0] = mat[5] = mat[10] = mat[15] = 1.0f;
}

void mat_copy(float* dest, float* src) { memcpy(dest, src, 16 * sizeof *dest); }

void mat_mul(float* res, float* m2)
{
    int i, j;
    float m1[16];

    memcpy(m1, res, sizeof m1);

    for (i = 0; i < 4; i++) {
        for (j = 0; j < 4; j++) {
            *res++ = m1[M(0, j)] * m2[M(i, 0)] + m1[M(1, j)] * m2[M(i, 1)]
                + m1[M(2, j)] * m2[M(i, 2)] + m1[M(3, j)] * m2[M(i, 3)];
        }
    }
}

void mat_translate(float* mat, float x, float y, float z)
{
    float m[] = { 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1 };
    m[12] = x;
    m[13] = y;
    m[14] = z;
    mat_mul(mat, m);
}

void mat_rotate(float* mat, float deg, float x, float y, float z)
{
    float m[] = { 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 };

    float angle = M_PI * deg / 180.0f;
    float sina = sin(angle);
    float cosa = cos(angle);
    float one_minus_cosa = 1.0f - cosa;
    float nxsq = x * x;
    float nysq = y * y;
    float nzsq = z * z;

    m[0] = nxsq + (1.0f - nxsq) * cosa;
    m[4] = x * y * one_minus_cosa - z * sina;
    m[8] = x * z * one_minus_cosa + y * sina;
    m[1] = x * y * one_minus_cosa + z * sina;
    m[5] = nysq + (1.0 - nysq) * cosa;
    m[9] = y * z * one_minus_cosa - x * sina;
    m[2] = x * z * one_minus_cosa - y * sina;
    m[6] = y * z * one_minus_cosa + x * sina;
    m[10] = nzsq + (1.0 - nzsq) * cosa;
    m[15] = 1.0f;

    mat_mul(mat, m);
}

void mat_perspective(float* mat, float vfov_deg, float aspect, float znear, float zfar)
{
    float m[] = { 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 };

    float vfov = M_PI * vfov_deg / 180.0f;
    float s = 1.0f / tan(vfov * 0.5f);
    float range = znear - zfar;

    m[0] = s / aspect;
    m[5] = s;
    m[10] = (znear + zfar) / range;
    m[11] = -1.0f;
    m[14] = 2.0f * znear * zfar / range;

    mat_mul(mat, m);
}

void mat_transform(float* mat, float* vec)
{
    float x = mat[0] * vec[0] + mat[4] * vec[1] + mat[8] * vec[2] + mat[12];
    float y = mat[1] * vec[0] + mat[5] * vec[1] + mat[9] * vec[2] + mat[13];
    float z = mat[2] * vec[0] + mat[6] * vec[1] + mat[10] * vec[2] + mat[14];

    vec[0] = x;
    vec[1] = y;
    vec[2] = z;
}

void cleanup(void)
{
    free(torus.varr);
    free(torus.iarr);
    if (torus.vbo) {
        glDeleteBuffers(1, &torus.vbo);
        glDeleteBuffers(1, &torus.ibo);
    }
    if (torus.vao) {
        glDeleteVertexArrays(1, &torus.vao);
    }
    glDeleteTextures(1, &g_tex);
    glDeleteBuffers(1, &ubo_matrix);
}

void display(void)
{
    matrix_state.lpos[0] = -10;
    matrix_state.lpos[1] = 10;
    matrix_state.lpos[2] = 10;

    glClearColor(0.05, 0.05, 0.05, 1.0);
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);

    mat_identity(matrix_state.view_mat);
    mat_translate(matrix_state.view_mat, 0, 0, -cam_dist);
    mat_rotate(matrix_state.view_mat, cam_phi, 1, 0, 0);
    mat_rotate(matrix_state.view_mat, cam_theta, 0, 1, 0);

    mat_copy(matrix_state.mvmat, matrix_state.view_mat);

    mat_copy(matrix_state.mvpmat, matrix_state.proj_mat);
    mat_mul(matrix_state.mvpmat, matrix_state.mvmat);

    mat_transform(matrix_state.view_mat, matrix_state.lpos);

    glUseProgram(g_sdr);

    glBindBuffer(GL_UNIFORM_BUFFER, ubo_matrix);
    glBufferSubData(GL_UNIFORM_BUFFER, 0, sizeof matrix_state, &matrix_state);
    glBindBufferBase(GL_UNIFORM_BUFFER, UBLOCK_MATRIX, ubo_matrix);

    glBindTexture(GL_TEXTURE_2D, g_tex);
    draw_mesh(&torus);

    assert(glGetError() == GL_NO_ERROR);
    glutSwapBuffers();
}

void reshape(int x, int y)
{
    glViewport(0, 0, x, y);

    mat_identity(matrix_state.proj_mat);
    mat_perspective(matrix_state.proj_mat, 50.0, (float)x / (float)y, 0.5, 500.0);
}

void keypress(unsigned char key, int x, int y)
{
    switch (key) {
    case 27:
        exit(0);
    }
}

void mouse(int bn, int st, int x, int y)
{
    bnstate[bn - GLUT_LEFT_BUTTON] = st == GLUT_DOWN ? 1 : 0;
    prev_x = x;
    prev_y = y;
}

void motion(int x, int y)
{
    int dx = x - prev_x;
    int dy = y - prev_y;
    prev_x = x;
    prev_y = y;

    if (!dx && !dy)
        return;

    if (bnstate[0]) {
        cam_theta += dx * 0.5;
        cam_phi += dy * 0.5;
        if (cam_phi < -90)
            cam_phi = -90;
        if (cam_phi > 90)
            cam_phi = 90;
        glutPostRedisplay();
    }
    if (bnstate[2]) {
        cam_dist += dy * 0.1;
        if (cam_dist < 0.0)
            cam_dist = 0.0;
        glutPostRedisplay();
    }
}

static void torus_vertex(struct vertex* vout, float rad, float rrad, float u, float v)
{
    float theta = u * M_PI * 2.0;
    float phi = v * M_PI * 2.0;
    float rx, ry, rz, cx, cy, cz;

    cx = sin(theta) * rad;
    cy = 0.0;
    cz = -cos(theta) * rad;

    rx = -cos(phi) * rrad + rad;
    ry = sin(phi) * rrad;
    rz = 0.0;

    vout->x = rx * sin(theta) + rz * cos(theta);
    vout->y = ry;
    vout->z = -rx * cos(theta) + rz * sin(theta);

    vout->nx = (vout->x - cx) / rrad;
    vout->ny = (vout->y - cy) / rrad;
    vout->nz = (vout->z - cz) / rrad;

    vout->tu = u;
    vout->tv = v;
}

int gen_torus(struct mesh* mesh, float rad, float rrad, int usub, int vsub)
{
    int i, j, uverts, vverts, nverts, nquads, ntri;
    float u, v;
    float du = 1.0 / (float)usub;
    float dv = 1.0 / (float)vsub;
    struct vertex* vptr;
    unsigned int* iptr;

    if (usub < 3)
        usub = 3;
    if (vsub < 3)
        vsub = 3;

    uverts = usub + 1;
    vverts = vsub + 1;

    nverts = uverts * vverts;
    nquads = usub * vsub;
    ntri = nquads * 2;

    mesh->vcount = nverts;
    mesh->icount = ntri * 3;

    if (!(mesh->varr = (vertex*)malloc(mesh->vcount * sizeof *mesh->varr))) {
        fprintf(stderr, "failed to allocate vertex array for %d vertices\n", mesh->vcount);
        return -1;
    }
    vptr = mesh->varr;
    if (!(mesh->iarr = (unsigned int*)malloc(mesh->icount * sizeof *mesh->iarr))) {
        fprintf(stderr, "failed to allocate index array for %d indices\n", mesh->icount);
        free(mesh->varr);
        mesh->varr = 0;
        return -1;
    }
    iptr = mesh->iarr;

    u = 0.0;
    for (i = 0; i < uverts; i++) {
        v = 0.0;
        for (j = 0; j < vverts; j++) {
            torus_vertex(vptr++, rad, rrad, u, v);

            if (i < usub && j < vsub) {
                int vnum = i * vverts + j;
                *iptr++ = vnum;
                *iptr++ = vnum + vverts + 1;
                *iptr++ = vnum + 1;
                *iptr++ = vnum;
                *iptr++ = vnum + vverts;
                *iptr++ = vnum + vverts + 1;
            }

            v += dv;
        }
        u += du;
    }

    glGenBuffers(1, &mesh->vbo);
    glBindBuffer(GL_ARRAY_BUFFER, mesh->vbo);
    glBufferData(GL_ARRAY_BUFFER, mesh->vcount * sizeof *mesh->varr, mesh->varr, GL_STATIC_DRAW);
    glBindBuffer(GL_ARRAY_BUFFER, 0);

    glGenBuffers(1, &mesh->ibo);
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, mesh->ibo);
    glBufferData(
        GL_ELEMENT_ARRAY_BUFFER, mesh->icount * sizeof *mesh->iarr, mesh->iarr, GL_STATIC_DRAW);
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0);

    glGenVertexArrays(1, &mesh->vao);
    glBindVertexArray(mesh->vao);

    glEnableVertexAttribArray(VATTR_VERTEX);
    glEnableVertexAttribArray(VATTR_NORMAL);
    glEnableVertexAttribArray(VATTR_TEXCOORD);

    glBindBuffer(GL_ARRAY_BUFFER, mesh->vbo);
    glVertexAttribPointer(VATTR_VERTEX, 3, GL_FLOAT, GL_FALSE, sizeof(struct vertex), 0);
    glVertexAttribPointer(VATTR_NORMAL, 3, GL_FLOAT, GL_FALSE, sizeof(struct vertex),
        (void*)offsetof(struct vertex, nx));
    glVertexAttribPointer(VATTR_TEXCOORD, 2, GL_FLOAT, GL_FALSE, sizeof(struct vertex),
        (void*)offsetof(struct vertex, tu));
    glBindBuffer(GL_ARRAY_BUFFER, 0);

    glBindVertexArray(0);
    return 0;
}

void draw_mesh(struct mesh* mesh)
{
    glBindVertexArray(mesh->vao);

    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, mesh->ibo);
    glDrawElements(GL_TRIANGLES, mesh->icount, GL_UNSIGNED_INT, 0);
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0);

    glBindVertexArray(0);
}

unsigned int gen_texture(int width, int height)
{
    int i, j;
    unsigned int tex;
    unsigned char *pixels, *ptr;

    if (!(pixels = (unsigned char*)malloc(width * height * 3))) {
        return 0;
    }
    ptr = pixels;

    for (i = 0; i < height; i++) {
        for (j = 0; j < width; j++) {
            int x = i ^ j;
            *ptr++ = x;
            *ptr++ = (x << 1) & 0xff;
            *ptr++ = (x << 2) & 0xff;
        }
    }

    glGenTextures(1, &tex);
    glBindTexture(GL_TEXTURE_2D, tex);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, pixels);
    glGenerateMipmap(GL_TEXTURE_2D);

    free(pixels);
    return tex;
}

unsigned int load_shader(const char* fname, int type)
{
    unsigned int sdr;
    int fsz;
    char* buf;
    FILE* fp;
    int status, loglen;

    if (!(fp = fopen(fname, "rb"))) {
        fprintf(stderr, "failed to open shader: %s\n", fname);
        return 0;
    }
    fseek(fp, 0, SEEK_END);
    fsz = ftell(fp);
    rewind(fp);

    if (!(buf = (char*)malloc(fsz + 1))) {
        fprintf(stderr, "failed to allocate %d bytes\n", fsz + 1);
        fclose(fp);
        return 0;
    }
    if (fread(buf, 1, fsz, fp) < (size_t)fsz) {
        fprintf(stderr, "failed to read shader: %s\n", fname);
        free(buf);
        fclose(fp);
        return 0;
    }
    buf[fsz] = 0;
    fclose(fp);

    sdr = glCreateShader(type);

#ifndef SPIRV
    glShaderSource(sdr, 1, (const char**)&buf, 0);
    glCompileShader(sdr);
#else
    glShaderBinary(1, &sdr, GL_SHADER_BINARY_FORMAT_SPIR_V_ARB, buf, fsz);
    gl_specialize_shader(sdr, "main", 0, 0, 0);
#endif
    free(buf);

    glGetShaderiv(sdr, GL_COMPILE_STATUS, &status);
    if (status) {
        printf("successfully compiled shader: %s\n", fname);
    } else {
        printf("failed to compile shader: %s\n", fname);
    }

    glGetShaderiv(sdr, GL_INFO_LOG_LENGTH, &loglen);
    if (loglen > 0 && (buf = (char*)malloc(loglen + 1))) {
        glGetShaderInfoLog(sdr, loglen, 0, buf);
        buf[loglen] = 0;
        printf("%s\n", buf);
        free(buf);
    }

    if (!status) {
        glDeleteShader(sdr);
        return 0;
    }
    return sdr;
}

unsigned int load_program(const char* vfname, const char* pfname)
{
    unsigned int vs, ps, prog;

    if (!(vs = load_shader(vfname, GL_VERTEX_SHADER))) {
        return 0;
    }
    if (!(ps = load_shader(pfname, GL_FRAGMENT_SHADER))) {
        glDeleteShader(vs);
        return 0;
    }

    prog = glCreateProgram();
    glAttachShader(prog, vs);
    glAttachShader(prog, ps);

    if (link_program(prog) == -1) {
        glDeleteShader(vs);
        glDeleteShader(ps);
        glDeleteProgram(prog);
        return 0;
    }

    glDetachShader(prog, vs);
    glDetachShader(prog, ps);

    return prog;
}

int link_program(unsigned int prog)
{
    int status, loglen;
    char* buf;

    glLinkProgram(prog);

    glGetProgramiv(prog, GL_LINK_STATUS, &status);
    if (status) {
        printf("successfully linked shader program\n");
    } else {
        printf("failed to link shader program\n");
    }

    glGetProgramiv(prog, GL_INFO_LOG_LENGTH, &loglen);
    if (loglen > 0 && (buf = (char*)malloc(loglen + 1))) {
        glGetProgramInfoLog(prog, loglen, 0, buf);
        buf[loglen] = 0;
        printf("%s\n", buf);
        free(buf);
    }

    return status ? 0 : -1;
}

const char* gldebug_srcstr(unsigned int src)
{
    switch (src) {
    case GL_DEBUG_SOURCE_API:
        return "api";
    case GL_DEBUG_SOURCE_WINDOW_SYSTEM:
        return "wsys";
    case GL_DEBUG_SOURCE_SHADER_COMPILER:
        return "sdrc";
    case GL_DEBUG_SOURCE_THIRD_PARTY:
        return "3rdparty";
    case GL_DEBUG_SOURCE_APPLICATION:
        return "app";
    case GL_DEBUG_SOURCE_OTHER:
        return "other";
    default:
        break;
    }
    return "unknown";
}

const char* gldebug_typestr(unsigned int type)
{
    switch (type) {
    case GL_DEBUG_TYPE_ERROR:
        return "error";
    case GL_DEBUG_TYPE_DEPRECATED_BEHAVIOR:
        return "deprecated";
    case GL_DEBUG_TYPE_UNDEFINED_BEHAVIOR:
        return "undefined behavior";
    case GL_DEBUG_TYPE_PORTABILITY:
        return "portability";
    case GL_DEBUG_TYPE_PERFORMANCE:
        return "performance";
    case GL_DEBUG_TYPE_OTHER:
        return "other";
    default:
        break;
    }
    return "unknown";
}

void GLAPIENTRY gldebug(GLenum src, GLenum type, GLuint id, GLenum severity, GLsizei len,
    const char* msg, const void* cls)
{
    printf("[GLDEBUG] (%s) %s: %s\n", gldebug_srcstr(src), gldebug_typestr(type), msg);
}

int init(void)
{
    glDebugMessageCallback(gldebug, 0);
    glEnable(GL_DEPTH_TEST);
    glEnable(GL_CULL_FACE);

    gl_specialize_shader
        = (PFNGLSPECIALIZESHADERPROC)glXGetProcAddress((unsigned char*)"glSpecializeShaderARB");
    if (!gl_specialize_shader) {
        fprintf(stderr, "failed to load glSpecializeShaderARB entry point\n");
        return -1;
    }

    if (!(g_tex = gen_texture(256, 256))) {
        return -1;
    }

    if (gen_torus(&torus, 1.0, 0.25, 32, 12) == -1) {
        return -1;
    }

#ifdef SPIRV
    if (!(g_sdr = load_program(SHADERDIR "vertex.spv", SHADERDIR "pixel.spv"))) {
        return -1;
    }
#else
    if (!(g_sdr = load_program(SHADERDIR "vertex.glsl", SHADERDIR "pixel.glsl"))) {
        return -1;
    }
#endif

    glUseProgram(g_sdr);

    glGenBuffers(1, &ubo_matrix);
    glBindBuffer(GL_UNIFORM_BUFFER, ubo_matrix);
    glBufferData(GL_UNIFORM_BUFFER, sizeof matrix_state, &matrix_state, GL_STREAM_DRAW);

    return 0;
}

int main(int argc, char** argv)
{
    glutInit(&argc, argv);
    glutInitWindowSize(800, 600);
    glutInitDisplayMode(GLUT_RGB | GLUT_DEPTH | GLUT_DOUBLE);
    glutInitContextProfile(GLUT_CORE_PROFILE);
    glutInitContextVersion(4, 4);
    glutCreateWindow("GL4 test");

    glutDisplayFunc(display);
    glutReshapeFunc(reshape);
    glutKeyboardFunc(keypress);
    glutMouseFunc(mouse);
    glutMotionFunc(motion);

    if (init() == -1) {
        return 1;
    }
    atexit(cleanup);

    glutMainLoop();
    return 0;
}
