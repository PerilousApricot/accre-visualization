#!/usr/bin/env python
"""
ACCRE Visualization
    - visualization for cluster status
"""



#
# This code was created by Richard Campbell '99 (ported to Python/PyOpenGL by John Ferguson and Tony Colston 2000)
# To be honst I stole all of John Ferguson's code and just added the changed stuff for lesson 5. So he did most
# of the hard work.

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import sys
import zmq
import math
import json
import socket
import struct
from VisibleObject import VisibleObject
OpenGL.FULL_LOGGING = True

def WriteText( text ):
    glPushMatrix()
    glScalef(0.0005,0.0005,0.0005)
    for char in text:
        glutStrokeCharacter(GLUT_STROKE_MONO_ROMAN, ord(char))
    glPopMatrix()

class NodeBox( VisibleObject ):
    def __init__(self, pos = 1,width = 1,height = 1, name = "Box", color = (0,1,0), isRotated=False ):
        self.pos = pos
        self.width = width
        self.height = height
        self.nodeList = []
        self.children = []
        self.name = name
        self.color = color
        self.isRotated = isRotated
        VisibleObject.__init__(self, pos = pos)
    
    def addChild(self, *child):
        self.children.extend( child )
        

        
    def addNode(self, node):
        self.nodeList.append( node )
        shorter = min( self.width, self.height)
        longer  = max( self.width, self.height)
        spaceNeeded = len(self.nodeList)
        spaceProvided = 0
        subDivisions = 0
        while spaceNeeded > spaceProvided:
            subDivisions += 1
            spaceProvided = round(longer * subDivisions /shorter) * subDivisions

        print "need to fit is %s" % subDivisions
        # spend 20% of the interior on spacing
        spacing = shorter * 0.2
        spacerPerBox = spacing / (subDivisions + 1)
        boxAmount = shorter *0.8
        sizePerBox = boxAmount / (subDivisions)
        x,y = (  -1 * sizePerBox / 2, spacerPerBox + sizePerBox / 2)
        for node in self.nodeList:
            x += spacerPerBox + sizePerBox
            if x > shorter:
                y += spacerPerBox + sizePerBox
                x = spacerPerBox + sizePerBox / 2
            
            # nodes have global coordinates
            if shorter == self.width:
                node['pos'][0] = self.pos[0] + x
                node['pos'][1] = self.pos[1] + y
            else:
                node['pos'][0] = self.pos[0] + y
                node['pos'][1] = self.pos[1] + x
                
            node['size'] = sizePerBox/2
            
    def render(self):
        if not self.visible:
            return
        
        glPushMatrix()
        #glTranslate( *self.pos )
        
        # Draw the main box
        glColor( 0,0,0 )
        glBegin(GL_QUADS)
        glVertex3f( 0,0,0 )
        glVertex3f( self.width, 0,0)
        glVertex3f( self.width,self.height,0)
        glVertex3f( 0, self.height,0)
        glEnd()
        # Draw an outline
        glLineWidth(1)
        glColor( *self.color )
        glBegin(GL_LINE_STRIP)
        glVertex3f( 0,0,0.01 )
        glVertex3f( self.width, 0,0.01)
        glVertex3f( self.width,self.height,0.01)
        glVertex3f( 0, self.height,0.01)
        glVertex3f( 0,0,0.01 )
        glEnd()
        
        # Draw the name
        glColor( *self.color )
        glPushMatrix()
        glLineWidth(2)
        if self.isRotated:
            glRotate( 90, 0,0,1 )
            glTranslate( 0,0,.01)
            WriteText(self.name)
        else:
            glTranslate( 0,self.height,.01)
            WriteText(self.name)
        glPopMatrix()
        
        glLineWidth(1)
            
        # Draw the boxes
        glPopMatrix()
        