"""
VisibleObject - 
    Interface for all objects that are drawn

Created by Andrew Melo <andrew.melo@gmail.com> on Mar 31, 2012
"""
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

class VisibleObject:
    def __init__(self, pos = None):
        if pos:
            self.pos = pos
        else:
            self.pos = (0,0,0)
        
        self.children = []
        self.parent   = None
        self.visible  = True
        
    def setVisible(self):
        self.visible = True
    def setInvisible(self):
        self.visible = False
    
    def addChild(self, *children):
        self.children.extend( children )
    
    def renderAll(self):
        # helper function to render an obect and all its children
        if not self.visible:
            return
        glPushMatrix()
        glTranslatef( *self.pos )
        self.render()
        for child in self.children:
            child.renderAll()
        glPopMatrix()
        pass
    
    def render(self):
        pass        
    
    def updateAll(self, tick):
        self.update( tick )
        for child in self.children:
            child.updateAll( tick )
            
    def update(self, tick):
        pass
            