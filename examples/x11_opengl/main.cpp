// Based on
// https://www.khronos.org/opengl/wiki/Programming_OpenGL_in_Linux:_Creating_a_texture_from_a_Pixmap

#include <GL/gl.h>
#include <GL/glu.h>
#include <GL/glx.h>
#include <X11/Xlib.h>
#include <cstdio>
#include <cstdlib>
#include <iostream>
#include <string>

using namespace std::string_literals;

void Redraw(Display* dpy, Window win)
{
    XWindowAttributes gwa;

    XGetWindowAttributes(dpy, win, &gwa);
    glViewport(0, 0, gwa.width, gwa.height);
    glClearColor(0.3, 0.3, 0.3, 1.0);
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);

    glMatrixMode(GL_PROJECTION);
    glLoadIdentity();
    glOrtho(-1.25, 1.25, -1.25, 1.25, 1., 20.);

    glMatrixMode(GL_MODELVIEW);
    glLoadIdentity();
    gluLookAt(0., 0., 10., 0., 0., 0., 0., 1., 0.);

    glColor3f(1.0, 1.0, 1.0);

    glBegin(GL_QUADS);
    glTexCoord2f(0.0, 0.0);
    glVertex3f(-1.0, 1.0, 0.0);
    glTexCoord2f(1.0, 0.0);
    glVertex3f(1.0, 1.0, 0.0);
    glTexCoord2f(1.0, 1.0);
    glVertex3f(1.0, -1.0, 0.0);
    glTexCoord2f(0.0, 1.0);
    glVertex3f(-1.0, -1.0, 0.0);
    glEnd();

    glXSwapBuffers(dpy, win);
}

int main(int argc, char* argv[])
{
    GLint att[] = { GLX_RGBA, GLX_DEPTH_SIZE, 24, GLX_DOUBLEBUFFER, None };
    int pixmap_width = 128;
    int pixmap_height = 128;

    Display* dpy = XOpenDisplay(nullptr);
    if (dpy == nullptr) {
        std::cerr << "\n\t"s
                  << "cannot open display\n"s << std::endl;
        exit(0);
    }

    Window root = DefaultRootWindow(dpy);

    XVisualInfo* vi = glXChooseVisual(dpy, 0, att);
    if (vi == nullptr) {
        std::cerr << "\n\t"s
                  << "no appropriate visual found\n"s << std::endl;
        exit(0);
    }

    XSetWindowAttributes swa;
    swa.event_mask = ExposureMask | KeyPressMask;
    swa.colormap = XCreateColormap(dpy, root, vi->visual, AllocNone);

    Window win = XCreateWindow(dpy, root, 0, 0, 600, 600, 0, vi->depth, InputOutput, vi->visual,
        CWEventMask | CWColormap, &swa);
    XMapWindow(dpy, win);
    XStoreName(dpy, win, "PIXMAP TO TEXTURE");

    GLXContext glc = glXCreateContext(dpy, vi, nullptr, GL_TRUE);
    if (glc == nullptr) {
        std::cerr << "\n\t"s
                  << "cannot create gl context\n"s << std::endl;
        exit(0);
    }

    glXMakeCurrent(dpy, win, glc);
    glEnable(GL_DEPTH_TEST);

    // CREATE A PIXMAP AND DRAW SOMETHING

    Pixmap pixmap = XCreatePixmap(dpy, root, pixmap_width, pixmap_height, vi->depth);
    GC gc = DefaultGC(dpy, 0);

    XSetForeground(dpy, gc, 0x00c0c0);
    XFillRectangle(dpy, pixmap, gc, 0, 0, pixmap_width, pixmap_height);

    XSetForeground(dpy, gc, 0x000000);
    XFillArc(dpy, pixmap, gc, 15, 25, 50, 50, 0, 360 * 64);

    XSetForeground(dpy, gc, 0x0000ff);

    auto msg = "PIXMAP TO TEXTURE"s;
    XDrawString(dpy, pixmap, gc, 10, 15, msg.c_str(), msg.length());

    XSetForeground(dpy, gc, 0xff0000);
    XFillRectangle(dpy, pixmap, gc, 75, 75, 45, 35);

    XFlush(dpy);

    XImage* xim = XGetImage(dpy, pixmap, 0, 0, pixmap_width, pixmap_height, AllPlanes, ZPixmap);

    if (xim == nullptr) {
        std::cerr << "\n\t"s
                  << "ximage could not be created.\n"s << std::endl;
    }

    // CREATE TEXTURE FROM PIXMAP

    GLuint texture_id;

    glEnable(GL_TEXTURE_2D);
    glGenTextures(1, &texture_id);
    glBindTexture(GL_TEXTURE_2D, texture_id);
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
    glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE);
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, pixmap_height, pixmap_height, 0, GL_RGBA,
        GL_UNSIGNED_BYTE, (void*)(&(xim->data[0])));

    XDestroyImage(xim);

    XEvent xev;
    while (true) {
        XNextEvent(dpy, &xev);
        if (xev.type == Expose) {
            Redraw(dpy, win);
        } else if (xev.type == KeyPress) {
            glXMakeCurrent(dpy, None, nullptr);
            glXDestroyContext(dpy, glc);
            XDestroyWindow(dpy, win);
            XCloseDisplay(dpy);
            exit(0);
        }
    }

    return EXIT_SUCCESS;
}
