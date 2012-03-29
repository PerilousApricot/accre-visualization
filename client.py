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
OpenGL.FULL_LOGGING = True

# Some api in the chain is translating the keystrokes to this octal string
# so instead of saying: ESCAPE = 27, we use the following.
ESCAPE = '\033'

# Number of the glut window.
window = 0

# Rotation angle for the triangle. 
rtri = 0.0

# Rotation angle for the quadrilateral.
rquad = 0.0

# A general OpenGL initialization function.  Sets all of the initial parameters. 
def InitGL(Width, Height):                # We call this right after our OpenGL window is created.
    glClearColor(0.0, 0.0, 0.0, 0.0)    # This Will Clear The Background Color To Black
    glClearDepth(1.0)                    # Enables Clearing Of The Depth Buffer
    glDepthFunc(GL_LESS)                # The Type Of Depth Test To Do
    glEnable(GL_DEPTH_TEST)                # Enables Depth Testing
    glShadeModel(GL_SMOOTH)                # Enables Smooth Color Shading
    
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()                    # Reset The Projection Matrix
                                        # Calculate The Aspect Ratio Of The Window
    gluPerspective(45.0, float(Width)/float(Height), 0.1, 100.0)

    glMatrixMode(GL_MODELVIEW)

# The function called when our window is resized (which shouldn't happen if you enable fullscreen, below)
def ReSizeGLScene(Width, Height):
    if Height == 0:                        # Prevent A Divide By Zero If The Window Is Too Small 
        Height = 1

    glViewport(0, 0, Width, Height)        # Reset The Current Viewport And Perspective Transformation
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45.0, 16.0/9.0, 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)

scene = { 'nodes' : [ ], 'blips' : [ ] }
storageElements = { }
storageDepots   = { }
clusterNodes    = { }
globalNodes     = { }
allNodes        = { }

def addToColumn( id, column, xpos ):
    global scene, allNodes
    oneDepot = { 'pos' : [xpos, 0.0,-1.0 ], 'color' : (1.0 ,0.2, 0.0), 'size' : 0.03, 'id' : id }
    column[id] = oneDepot
    scene['nodes'].append( oneDepot )
    allNodes[id] = oneDepot
    # rebalance the boxes
    # we have two units to work with
    depotCount = len( column )
    boxSize = 2.0 / depotCount
    index = 0.5
    for k in column:
        column[k]['size'] = boxSize * 0.2
        column[k]['pos'][1] = -1 + (index * boxSize)
        index += 1
        
def addNodeIfNeeded( id ):
    global storageElements, storageDepots, clusterNodes, allNodes, globalNodes
    if id in allNodes:
        return
    # fixme for real life
    if id < 16:
        addToColumn( id, storageElements, 1 )
    elif id < 25:
        addToColumn( id, storageDepots, 0 )
    elif id < 1000:
        addToColumn( id, clusterNodes, -1 )
    else:
        addToColumn( id, globalNodes, 1.75 )
            
    
# The main drawing function. 
currentTime = 0
def DrawGLScene():
    global scene, currentTime


    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)    # Clear The Screen And The Depth Buffer
    glLoadIdentity()                    # Reset The View
    glTranslate(0,0,-2)
    
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
    

    for node in scene['nodes']:
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
    
    for blip in scene['blips']:
        glColor3f( 1.0, 1.0, 1.0 )
        glPushMatrix()
        glTranslatef( *blip['pos'] )
        size = 0.01
        glBegin(GL_QUADS)
        glVertex3f(-size,  size, 0.0 )
        glVertex3f( size,  size, 0.0 )
        glVertex3f( size, -size, 0.0 )
        glVertex3f(-size, -size, 0.0 )
        glEnd()
        glPopMatrix()
        
        
        
    #  since this is double buffered, swap the buffers to display what just got drawn. 
    glutSwapBuffers()
    
def doIdle():
    global zsock,scene, currentTime
    updateDisplay = False   
    try:
        while True: #read everything! Bomb with done.
            trans = zsock.recv_json( zmq.NOBLOCK )
            processTransferInfo( trans )
            updateDisplay = True
    except zmq.ZMQError, e:
        pass
    
        
    thisTick    = glutGet(GLUT_ELAPSED_TIME)
    tick        = float(thisTick - currentTime) / 1000.0
    currentTime = thisTick
    
    blipList = []
    for blip in scene['blips']:
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
        
    scene['blips'] = blipList
        
    #if updateDisplay:
    glutPostRedisplay()

def processTransferInfo( transInfo ):
    if transInfo['type'] in ['bfsSend', 'gridftpDone']:
        addNodeIfNeeded( transInfo['from'] )
        addNodeIfNeeded( transInfo['to'] )
        displayTransferBlip( transInfo['from'], transInfo['to'], transInfo['size'] )
        
def displayTransferBlip( fromId, toId, size ):
    global allNodes
    # don't precache this because we want the blips to follow their target nodes
    scene['blips'].append( { 'pos' : allNodes[fromId]['pos'][:], 'target' : allNodes[toId], 'speed' : 0.5 } )

# The function called whenever a key is pressed. Note the use of Python tuples to pass in: (key, x, y)  
def keyPressed(*args):
    # If escape is pressed, kill everything.
    if args[0] == ESCAPE:
        glutDestroyWindow(window)
        sys.exit()

def main():
    global window

    glutInit(sys.argv)

    # Select type of Display mode:   
    #  Double buffer 
    #  RGBA color
    # Alpha components supported 
    # Depth buffer
    glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_ALPHA | GLUT_DEPTH)
    
    # get a 640 x 480 window 
    glutInitWindowSize(640, 480)
    
    # the window starts at the upper left corner of the screen 
    glutInitWindowPosition(0, 0)
    
    # Okay, like the C version we retain the window id to use when closing, but for those of you new
    # to Python (like myself), remember this assignment would make the variable local and not global
    # if it weren't for the global declaration at the start of main.
    window = glutCreateWindow("Jeff Molofee's GL Code Tutorial ... NeHe '99")

    # Register the drawing function with glut, BUT in Python land, at least using PyOpenGL, we need to
    # set the function pointer and invoke a function to actually register the callback, otherwise it
    # would be very much like the C version of the code.    
    glutDisplayFunc(DrawGLScene)
    #glutDisplayFunc()
    
    # Uncomment this line to get full screen.
    # glutFullScreen()

    # When we are doing nothing, redraw the scene.
    glutIdleFunc(doIdle)
        
    # Register the function called when our window is resized.
    glutReshapeFunc(ReSizeGLScene)

    # Register the function called when the keyboard is pressed.  
    glutKeyboardFunc(keyPressed)
    
    # Initialize our window. 
    InitGL(640, 480)

    
# Print message to console, and kick off the main to get it rolling.
print "Hit ESC key to quit."
if __name__ == '__main__':
    try:
        GLU_VERSION_1_2
    except:
        print "Need GLU 1.2 to run this demo"
        sys.exit(1)
    main()
    
    context = zmq.Context()
    zsock   = context.socket(zmq.SUB)
    zsock.connect("tcp://0.0.0.0:9898")
    zsock.setsockopt(zmq.SUBSCRIBE, "")
    glutMainLoop()
        
