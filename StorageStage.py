"""
StorageStage - 
    Stage showing the status of the cluster
    

Created by Andrew Melo <andrew.melo@gmail.com> on Apr 22, 2012
"""

import time, math
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

from VisibleObject import VisibleObject
from NodeBox import NodeBox
from TextBox import TextBox

def WriteText( text ):
    glPushMatrix()
    glScalef(0.001,0.001,0.001)
    for char in text:
        glutStrokeCharacter(GLUT_STROKE_MONO_ROMAN, ord(char))
    glPopMatrix()

class StorageStage( VisibleObject ):
    
    def __init__(self):
        # nashville's position on the earth
        # 46.3736798434 -814.257043345 595.764172455
        VisibleObject.__init__(self, pos = (45.9604490329, 580.455382799, 797.001287513))
        self.blips = []
        self.nodes = []
        seBox = NodeBox( (.2,-.6,-1), .23, 1.6, "StorageElements", (0.87,0.5,0.0), isRotated = True)
        depotBox   = NodeBox( (-.3,-0.6,-1), .1, 1.6, "Depots", (0.87,0.5,0.0), isRotated = True)
        clusterBox      = NodeBox( (-1.9,-0.1,-1), 1, 1, "VAMPIRE", (0.87,0.5,0.0))
        globalBox     = NodeBox( (1,0,-1), 0.9, 0.9, "External", (0.87,0.5,0.0))
        externalSpeedBox5 = NodeBox( (1, -0.9, -1), 0.9, 0.6, "GridFTP Transfers", (1,0,0) )
        externalSpeedBox60 = NodeBox( (1, -0.9, -1), 0.9, 0.6, "GridFTP Transfers", (1,0,0) )
        externalSpeedBox60.setInvisible()
        self.addChild( seBox, depotBox, clusterBox, globalBox, externalSpeedBox5, externalSpeedBox60 )
        
        inLabel5 = TextBox( pos = (0, 0.5, .01), color = (1,1,0), text = "Inbound (/5min)")
        inSpeed5 = TextBox( pos = (0, 0.4, .01), color = (1,1,0), text = "  100 MB/sec") 
        outLabel5 = TextBox( pos = (0, 0.3, .01), color = (1,1,0), text = "Outbound (/5min)")
        outSpeed5 = TextBox( pos = (0, 0.2, .01), color = (1,1,0), text = "  100 MB/sec")
        
        externalSpeedBox5.addChild( inLabel5, inSpeed5, outLabel5, outSpeed5)
        
        inLabel60 = TextBox( pos = (0, 0.5, .01), color = (1,1,0), text = "Inbound (/1hr)")
        inSpeed60 = TextBox( pos = (0, 0.4, .01), color = (1,1,0), text = "  100 MB/sec") 
        outLabel60 = TextBox( pos = (0, 0.3, .01), color = (1,1,0), text = "Outbound (/1hr)")
        outSpeed60 = TextBox( pos = (0, 0.2, .01), color = (1,1,0), text = "  100 MB/sec")
        
        externalSpeedBox60.addChild( inLabel60, inSpeed60, outLabel60, outSpeed60)
        
        self.externalSpeedBox5  = externalSpeedBox5
        self.externalSpeedBox60 = externalSpeedBox60
        self.inSpeed5 = inSpeed5
        self.inSpeed60 = inSpeed60
        self.outSpeed5 = outSpeed5
        self.outSpeed60 = outSpeed60        
        toggleGridftpBox = lambda x: self.toggleGridftpBox(x)
        
        glutTimerFunc(5000, toggleGridftpBox, 1)
        
        self.allNodes        = { }
        
        self.inboundGridftp  = []
        self.outboundGridftp = []
        
        
    def render(self):
        glPushMatrix()
        glTranslate(-2,1,-1)
        glColor3f(1.0,1.0,1.0)
        glLineWidth( 0.5 )
        WriteText("ACCRE Cluster Status")
        glPopMatrix()
        
        glLineWidth(1)
        glBegin(GL_LINES)
        glColor3f(0.5,0.5,1.0)
        for x in range(-20,21):
            x = x / 10.0
            glVertex3f(x,-1,-1.01)
            glVertex3f(x,1,-1.01)
            
        glColor3f(0.2,0.2,1.0)
        for x in range(-10,11):
            x = x / 10.0
            glVertex3f(-2,x,-1.01)
            glVertex3f(2,x,-1.01)
        glEnd()
        
        for node in self.nodes:
            glColor3f( *node['color'] )
            glPushMatrix()
            glTranslatef( *node['pos'] )
            size = node['size']
            glBegin(GL_QUADS)
            glVertex3f(-size,  size, 0.0 )
            glVertex3f( size,  size, 0.0 )
            glVertex3f( size, -size, 0.0 )
            glVertex3f(-size, -size, 0.0 )
            glEnd()
            glPopMatrix()
        
        for blip in self.blips:
            glColor3f( 1.0, 1.0, 1.0 )
            glPushMatrix()
            glTranslatef( *blip['pos'] )
            size = blip['size']
            glBegin(GL_QUADS)
            glVertex3f(-size,  size, 0.0 )
            glVertex3f( size,  size, 0.0 )
            glVertex3f( size, -size, 0.0 )
            glVertex3f(-size, -size, 0.0 )
            glEnd()
            glPopMatrix()
        
        inboundRate = self.computeAverageTransferRate( 60 * 5, self.inboundGridftp)
        self.inSpeed5.setText( "  %s/sec" % humanizeBytes(inboundRate))
        outboundRate = self.computeAverageTransferRate( 60 *  5, self.outboundGridftp)
        self.outSpeed5.setText("  %s/sec" % humanizeBytes(outboundRate))
        inboundRate = self.computeAverageTransferRate( 60 * 60, self.inboundGridftp)
        self.inSpeed60.setText( "  %s/sec" % humanizeBytes(inboundRate))
        outboundRate = self.computeAverageTransferRate( 60 * 60, self.outboundGridftp)
        self.outSpeed60.setText("  %s/sec" % humanizeBytes(outboundRate))
        #externalSpeedBox60.render()
        #externalSpeedBox5.render()
        #  since this is double buffered, swap the buffers to display what just got drawn. 
    
    def update(self, tick):
        blipList = []
        for blip in self.blips:
            # update position
            pos    = blip['pos']
            target = blip['target']['pos'] 
            speed  = blip['speed']
            length = math.sqrt( (pos[0] - target[0])*(pos[0] - target[0]) + \
                                (pos[1] - target[1])*(pos[1] - target[1]) + \
                                (pos[2] - target[2])*(pos[2] - target[2])  )
            
            if length < (tick * speed):
                continue
            pos[0] -= (pos[0] - target[0]) / length * ( speed * tick )
            pos[1] -= (pos[1] - target[1]) / length * ( speed * tick )
            pos[2] -= (pos[2] - target[2]) / length * ( speed * tick )
            blipList.append( blip )
            
        self.blips = blipList    
        
    def toggleGridftpBox( self, val ):
        global externalSpeedBox5, externalSpeedBox60, toggleGridftpBox
        toggleGridftpBoxJump = lambda x: self.toggleGridftpBox(x)
        if val == 1:
            self.externalSpeedBox5.setVisible()
            self.externalSpeedBox60.setInvisible()
            glutTimerFunc(5000, toggleGridftpBoxJump, 0)
        else:
            self.externalSpeedBox60.setVisible()
            self.externalSpeedBox5.setInvisible()
            glutTimerFunc(5000, toggleGridftpBoxJump, 1)
            
    def computeAverageTransferRate( self, period, transferList ):
        nBytes = 0
        currentTime = time.time()
        for xfer in transferList:
            if ( xfer[0] - xfer[3] ) > ( currentTime - period ):
                # transfer was entirely in the window
                nBytes += xfer[4]
            elif xfer[0] > ( currentTime - period ):
                # transfer was partially in the window
                nBytes += xfer[4] * ( xfer[0] - ( currentTime - period ) ) / xfer[3]
        return nBytes / period
    
    
def humanizeBytes( num ):
    suffix = ['B', 'KB', 'MB', 'GB']
    suffixBytes = 1
    for choice in suffix:
        suffixBytes *= 1000
        if suffixBytes > num:
            suffixBytes /= 1000
            return "%0.2f %s" % ( num/suffixBytes, choice)

    return "ERROR"
