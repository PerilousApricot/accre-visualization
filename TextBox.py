"""
TextBox - 
    Handles writing on screen

Created by Andrew Melo <andrew.melo@gmail.com> on Mar 30, 2012
"""
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from VisibleObject import VisibleObject

class TextBox( VisibleObject ):
    def __init__(self, pos,color,text):
        VisibleObject.__init__(self, pos = pos)
        self.color = color
        self.text = text
    
    def setPos(self, pos):
        self.pos = pos
    def setColor(self, color):
        self.color = color
    def setText(self, text):
        self.text = text
        
    def render(self):
        glPushMatrix()
        glColor( *self.color )
        glScalef(0.0005,0.0005,0.0005)
        for char in self.text:
            glutStrokeCharacter(GLUT_STROKE_MONO_ROMAN, ord(char))
        glPopMatrix()