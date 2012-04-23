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
import time
import socket
import struct
import Vectors
import NodeBox
import TextBox

from StorageStage import StorageStage
from CameraControl import CameraControl
from TexturedGlobe import TexturedGlobe
from CurlStage import CurlStage
from Timeline import *

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

scene = { 'objects' : [], 'camera' : CameraControl() }
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
    gluPerspective(45.0, float(Width)/float(Height), 0.1, 10000.0)

    glMatrixMode(GL_MODELVIEW)

# The function called when our window is resized (which shouldn't happen if you enable fullscreen, below)
def ReSizeGLScene(Width, Height):
    if Height == 0:                        # Prevent A Divide By Zero If The Window Is Too Small 
        Height = 1

    glViewport(0, 0, Width, Height)        # Reset The Current Viewport And Perspective Transformation
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45.0, float(Width)/float(Height), 0.1, 10000.0)
    glMatrixMode(GL_MODELVIEW)



seLookup = {'10.0.1.112' : 'se3.vampire', 
            '10.0.1.113' : 'se4.vampire',
            '10.0.1.114' : 'se5.vampire',
            '10.0.1.115' : 'se6.vampire',
            '10.0.1.116' : 'se7.vampire',
            '10.0.1.117' : 'se8.vampire',
            '10.0.1.118' : 'se9.vampire',
            '10.0.1.119' : 'se10.vampire',}
internalLookup = {}
internalLookup.update( seLookup )

seIds = []
allNodes = []
def addNodeIfNeeded( id ):
    return
    global allNodes, seBox, depotBox, clusterBox, otherBox, internalLookup, seIds
    global inLabel, outLabel
    if id in allNodes:
        return
    node = { 'pos' : [0, 0.0,-0.99 ], 'color' : (0.2 ,1.0, 0.0), 'size' : 0.03, 'id' : id }
    ipAddress = socket.inet_ntoa(struct.pack('!L',id))
    try:
        hostname  = socket.gethostbyaddr(ipAddress)[0]
    except:
        if ipAddress.startswith('10.'):
            if ipAddress in internalLookup:
                hostname = internalLookup[ipAddress]
            else:
                hostname = "unknown.vampire"
            print "Got the local hostname for ACCRE :/ Mapped %s to %s" % (ipAddress, hostname)
        else:
            print "Hostname wasn't found for ip %s. Probably due to testing. Overriding"
            hostname= "otherhost.cern.ch"
        
    allNodes[id] = node
    scene['nodes'].append( node )
    print "Got a new node. id: %s ip %s hostname %s" % (id, ipAddress, hostname)
    # fixme for real life
    if (not hostname.endswith('accre.vanderbilt.edu')) and \
       (not hostname.endswith('.vampire')):
        print "  called it a global node"
        globalBox.addNode( node )
    elif hostname.startswith('se'):
        print "  called it a storage element"
        seIds.append( id )
        seBox.addNode( node )
    elif hostname.startswith('cms-depot'):
        print "  called it a depot"
        depotBox.addNode( node )
    elif hostname.startswith('vmp'):
        print "  called it a cluster node"
        clusterBox.addNode( node )
    elif hostname == "monitor.accre.vanderbilt.edu":
        print "  called it the nagios host"
        clusterBox.addNode( node )
    else:
        print "Got a strange hostname %s" % hostname
        clusterBox.addNode( node )



# The main drawing function. 
currentTime = 0
def DrawGLScene():
    global scene, currentTime, inboundGridftp, outboundGridftp
    global inSpeed5, outSpeed5, inSpeed60, outSpeed60
    updateScene()

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)    # Clear The Screen And The Depth Buffer
    glLoadIdentity()                    # Reset The View
    scene['camera'].setCamera()
    for stage in scene['objects']:
        stage.renderAll()
    glutSwapBuffers()
    glutPostRedisplay()


def doIdle():
    global zsock,scene, currentTime
    time.sleep(0.01)
    return
    try:
        while True: #read everything! Bomb with done.
            trans = zsock.recv_json( zmq.NOBLOCK )
            processTransferInfo( trans )
            updateDisplay = True
    except zmq.ZMQError, e:
        # slowwwww dowwwwnnn
        time.sleep(0.01)
        pass

def updateScene():    
    global currentTime, scene
    thisTick    = glutGet(GLUT_ELAPSED_TIME)
    tick        = float(thisTick - currentTime) / 1000.0
    currentTime = thisTick
    
    for stage in scene['objects']:
        stage.updateAll( tick )
    
    if scene['currentTimeline']:
        scene['currentTimeline'].update( currentTime )
        if scene['currentTimeline'].isDone() and scene['currentTimeline'].getNext():
            scene['currentTimeline'] = scene['currentTimeline'].getNext()
            scene['currentTimeline'].start( currentTime )


def processTransferInfo( transInfo ):
    global seIds, inboundGridftp, outboundGridftp
    if transInfo['type'] in ['bfsSend', 'gridftpDone']:
        addNodeIfNeeded( transInfo['from'] )
        addNodeIfNeeded( transInfo['to'] )
        duration = 1
        if 'duration' in transInfo:
            duration = transInfo['duration']
        if duration == 0:
            duration = 1
            
        speed = transInfo['size'] / duration
        displayTransferBlip( transInfo['from'], transInfo['to'], transInfo['size'], speed )
        
        print "transfer %s -> %s" % (transInfo['from'], transInfo['to'])
        if transInfo['type'] == 'gridftpDone':
            if transInfo['from'] in seIds:
                # outbound
                outboundGridftp.append( [time.time(), transInfo['from'], transInfo['to'], transInfo['duration'], transInfo['size']])
            else:
                inboundGridftp.append( [time.time(), transInfo['from'], transInfo['to'], transInfo['duration'], transInfo['size']])
            
        
def displayTransferBlip( fromId, toId, size, speed = 0 ):
    global allNodes
    
    # make larger transfers bigger
    if size < 1024*1024:
        blipSize = 0.01
    elif size < 1024*1024*1024:
        blipSize = 0.02
    else:
        blipSize = 0.04
    
    # make speedier transfers faster    
    if speed < 1024*1024:
        blipSpeed = 0.25
    elif speed > 1024*1024*1024:
        blipSpeed = 0.75
    else:
        blipSpeed =  ( 0.75 - 0.25 ) / ( 1024*1024*1024 - 1024*1024 ) * speed + 0.25
    
    # don't precache this because we want the blips to follow their target nodes

    scene['blips'].append( { 'pos' : allNodes[fromId]['pos'][:], 'target' : allNodes[toId],
                             'speed' : blipSpeed,
                             'size' : blipSize } )

mapHandle = None
def loadMap():
    global mapHandle
    

# The function called whenever a key is pressed. Note the use of Python tuples to pass in: (key, x, y)  
def keyPressed(*args):
    global scene
    # If escape is pressed, kill everything.
    if args[0] == ESCAPE:
        glutDestroyWindow(window)
        sys.exit()
    if args[0] == 'q':
        scene['currentTimeline'] = None
        print "test"
        
    if args[0] == 'n':
        if scene['currentTimeline']:
            scene['currentTimeline'].update( currentTime )
            if scene['currentTimeline'].getNext():
                scene['currentTimeline'] = scene['currentTimeline'].getNext()
                scene['currentTimeline'].start( currentTime )

def mousePressed( button, state, x, y ):
    global scene
    print "Mouse corrds %s camera %s" % (gluUnProject(x,y,0.0), scene['camera'].pos)
           
def main():
    global window, scene

    glutInit(sys.argv)

    # Select type of Display mode:   
    #  Double buffer 
    #  RGBA color
    # Alpha components supported 
    # Depth buffer
    glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_ALPHA | GLUT_DEPTH)
    
    # get a 640 x 480 window 
    glutInitWindowSize(960, 480)
    
    # the window starts at the upper left corner of the screen 
    glutInitWindowPosition(0, 0)
    
    # Okay, like the C version we retain the window id to use when closing, but for those of you new
    # to Python (like myself), remember this assignment would make the variable local and not global
    # if it weren't for the global declaration at the start of main.
    window = glutCreateWindow("ACCRE Cluster Status Monitor")

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
    
    glutMouseFunc( mousePressed )
    
    # Load the stages
    storageStage   = StorageStage()
    globeStage     = TexturedGlobe()

    LHCStatusStage = CurlStage( pos = [40.9604490329, 580.455382799, 797.001287513],
                                url = "http://vistar-capture.web.cern.ch/vistar-capture/lhc1.png",
                                updateRate = 160 * 1000)
    DAQStatusStage = CurlStage( pos = [36.9604490329, 580.455382799, 797.001287513],
                                url = "http://cmsonline.cern.ch/daqStatusSCX/aDAQmon/DAQstatusGre.jpg",
                                updateRate = 150 * 1000)
    CMSStatusStage = CurlStage( pos = [32.9604490329, 580.455382799, 797.001287513],
                                url = "http://cmspage1.web.cern.ch/cmspage1/data/page1.png",
                                updateRate = 180 * 1000)
    
    scene['camera'].lookat = LHCStatusStage.pos
    scene['camera'].pos = [40.9604490329, 580.455382799, 799.001287513]
     
    scene['objects'].extend( [storageStage, globeStage, LHCStatusStage, DAQStatusStage, CMSStatusStage] )
    
    globalCameraTween    = MoveCameraTween( scene['camera'], [137.74360349518597, 1769.5965518451512, 2418.585277263117],
                                            [0,0,0],[0,1,0] )
    
    #globalViewTween = RotateCameraTween( scene['camera'], 36.1658, -86.7844, 3000, 1, [0,0,0], [0,1,0])
    globalViewTween = RotateCameraTween( scene['camera'], 36.1658,-86.7844, 3000, 1, [0,0,0], [0,1,0])

    storageCamTween  = MoveCameraTween( scene['camera'],
                                             [45.9604490329, 580.455382799, 799.001287513],
                                             [45.9604490329, 580.455382799, 797.001287513],
                                             [0,1,0] )

    
    hideGlobe = HideTween( [ globeStage] )
    showGlobe = ShowTween( [ globeStage] )
    
    storageTimeline = Timeline( name = "Vampire - Storage")
    storageTimeline.tweens.append( storageCamTween )
    storageTimeline.tweens.append( hideGlobe )
    storageToGlobal = Timeline( name = "Zoom to world")
    storageToGlobal.tweens.append( globalCameraTween )
    storageToGlobal.tweens.append( showGlobe )
    globalTimeline  = Timeline( name = "CMS - Global")
    globalTimeline.tweens.append( globalViewTween )
    #globalTimeline.duration = 50000
    globalToStorage = Timeline( name = "Zoom to ACCRE")
    globalToStorage.tweens.append( storageCamTween )
    
    plotsToMonitor = ["http://vistar-capture.web.cern.ch/vistar-capture/lhc1.png",
                      "http://cmsonline.cern.ch/daqStatusSCX/aDAQmon/DAQstatusGre.jpg",
                      "http://cmspage1.web.cern.ch/cmspage1/data/page1.png"]
    initialPlotPos = [40.9604490329, 580.455382799, 797.001287513]
    previousTimeline = storageTimeline
    for plot in plotsToMonitor:
        stage = CurlStage( pos = initialPlotPos,
                                url = plot,
                                updateRate = 160 * 1000)
        
        plotSwapTween  = MoveCameraTween( scene['camera'],
                                             Vectors.add(stage.pos, [0,0,2]),
                                             stage.pos,
                                             [0,1,0],
                                             arrivalAlpha = 0.1 )
        currentTimeline = Timeline( name = "Monitoring Plots")
        currentTimeline.tweens.append( plotSwapTween )
        previousTimeline.setNext( currentTimeline )
        previousTimeline = currentTimeline
        initialPlotPos = Vectors.add(initialPlotPos, [-4,0,0])

    currentTimeline.setNext(storageToGlobal)
    storageToGlobal.setNext( globalTimeline )
    globalTimeline.setNext(  globalToStorage )
    globalToStorage.setNext( storageTimeline )
    
    scene['currentTimeline'] = globalTimeline
    globalTimeline.start( 0 )
    # Initialize our window. 
    InitGL(960, 480)

    
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
    zsock.connect("tcp://se2.accre.vanderbilt.edu:9898")
    zsock.setsockopt(zmq.SUBSCRIBE, "")
    glutMainLoop()
        
