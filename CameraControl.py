"""
CameraControl - 
    Wraps functionality around the camera

Created by Andrew Melo <andrew.melo@gmail.com> on Apr 22, 2012
"""
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *
class CameraControl:
    
    def __init__(self):
        self.pos = (3000,0,0)
        self.lookat = (0,0,0)
        self.up = (0,1,0)

    def setCamera(self):
        glLoadIdentity()
        glutSetWindowTitle( "(%.1f %.1f %.1f)->(%.1f %.1f %.1f)" % (self.pos[0], self.pos[1], self.pos[2], 
                   self.lookat[0], self.lookat[1], self.lookat[2]) )
        
        gluLookAt( self.pos[0], self.pos[1], self.pos[2], 
                   self.lookat[0], self.lookat[1], self.lookat[2],
                   self.up[0], self.up[1], self.up[2])
        
