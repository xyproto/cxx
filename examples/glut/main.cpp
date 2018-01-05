#include <cstdlib>

#ifdef __APPLE__
#include <GLUT/glut.h>
#else
#include <GL/glut.h>
#endif

void displayMe(void) {
  glClear(GL_COLOR_BUFFER_BIT);
  glBegin(GL_POLYGON);

  glVertex3f(0.0, 0.0, 0.0);
  glVertex3f(0.5, 0.0, 0.0);
  glVertex3f(0.5, 0.5, 0.0);
  glVertex3f(0.0, 0.5, 0.0);

  glEnd();
  glFlush();
}

void processKeys(unsigned char key, int x, int y) {
  // Quit if Esc or q was pressed
  if (key == 27 || key == 113) {
    exit(EXIT_SUCCESS);
  }
}

int main(int argc, char** argv) {
  glutInit(&argc, argv);
  glutInitDisplayMode(GLUT_SINGLE);
  glutInitWindowSize(320, 200);
  glutInitWindowPosition(200, 200);
  glutCreateWindow("Hello, World!");
  glutKeyboardFunc(processKeys);
  glutDisplayFunc(displayMe);
  glutMainLoop();
  return 0;
}
