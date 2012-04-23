"""
CurlStage - 
    Downloads an arbitrary file from a webpage and displays it

Created by Andrew Melo <andrew.melo@gmail.com> on Apr 22, 2012
"""

try:
    import Image
except ImportError:
    from PIL import Image
    
import time, math, hashlib
import os.path
import urllib
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

from VisibleObject import VisibleObject
import Vectors
# http://vistar-capture.web.cern.ch/vistar-capture/lhc1.png
# http://cmspage1.web.cern.ch/cmspage1/data/page1.png
# http://cmsonline.cern.ch/daqStatusSCX/aDAQmon/DAQstatusGre.jpg
class CurlStage( VisibleObject ):
    
    def __init__(self, pos, url, updateRate):
        # nashville's position on the earth
        # 46.3736798434 -814.257043345 595.764172455
        VisibleObject.__init__(self, pos = pos)
        self.url  = url
        self.updateRate = updateRate
        self.textureGL = None
        self.topLeft     = None
        self.bottomRight = None
        self.width  = 1
        self.height = 1
        
        updateLambda = lambda x: self.updateImage(x)
        glutTimerFunc(0, updateLambda, 1)
    
    def updateImage(self, dummy):
        try:
            local = "%s.cache" % hashlib.md5( self.url ).hexdigest()
            if not os.path.exists( local ) or os.path.getmtime ( local ) < (time.time() - self.updateRate/1000):
                print "Retrieving %s " % self.url  
                urllib.urlretrieve( self.url, local )
            im = Image.open( local )
            try:
                # get image meta-data (dimensions) and data
                ix, iy, image = im.size[0], im.size[1], im.tostring("raw", "RGBA", 0, -1)
            except SystemError:
                # has no alpha channel, synthesize one, see the
                # texture module for more realistic handling
                ix, iy, image = im.size[0], im.size[1], im.tostring("raw", "RGBX", 0, -1)
            
            print "Texture is this size %s %s" % (ix, iy) 
            # generate a texture ID
            ID = glGenTextures(1)
            # make it current
            glBindTexture(GL_TEXTURE_2D, ID)
            glPixelStorei(GL_UNPACK_ALIGNMENT,1)
            # copy the texture into the current texture ID
            glTexImage2D(GL_TEXTURE_2D, 0, 3, ix, iy, 0, GL_RGBA, GL_UNSIGNED_BYTE, image)
            self.imageWidth  = ix
            self.imageHeight = iy
            # return the ID for use
            self.textureGL = ID
        except Exception, e:
            print "Error, couldn't load (%s): %s" % (self.url, e)
            
    def calcCorners(self):
        """
        assumes we'll be facing from 2 units away on the z axis
        """
        targetZ = 2
        screenWidth = glutGet(GLUT_WINDOW_WIDTH)
        screenHeight = glutGet(GLUT_WINDOW_HEIGHT)
        fov = 45.0 / 360.0 * ( 2.0 * 3.14 )
        worldHeight = targetZ * math.tan( fov / 2 )
        worldWidth  = worldHeight * float( self.imageWidth ) / float( self.imageHeight )
        
        scaledWidth = self.width * worldWidth / self.height / 2
        quadCenter = [0,0,0]
        self.topLeft     = Vectors.add( quadCenter, [-worldWidth, worldHeight, 0])
        self.topRight    = Vectors.add( quadCenter, [ worldWidth, worldHeight, 0])        
        self.bottomRight = Vectors.add( quadCenter, [ worldWidth,-worldHeight, 0])
        self.bottomLeft  = Vectors.add( quadCenter, [-worldWidth,-worldHeight, 0])
        
        print "w %s %s %s %s %s %s" % (screenWidth, screenHeight, fov, worldHeight, worldWidth, scaledWidth)
        print " %s\n %s\n %s\n %s\n" % (self.topLeft,
                                        self.topRight,  
                                        self.bottomRight,
                                        self.bottomLeft)
            
    def render(self):
        if not self.bottomRight:
            self.calcCorners()
        if self.textureGL:
            glEnable(GL_TEXTURE_2D)
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)
            glBindTexture(GL_TEXTURE_2D, self.textureGL)
        else:
            glColor3f(1,1,0)
            
        glBegin(GL_QUADS)
        glTexCoord2f(0.0,1.0);glVertex3f(*self.topLeft)
        glTexCoord2f(1.0,1.0);glVertex3f(*self.topRight)
        glTexCoord2f(1.0,0.0);glVertex3f(*self.bottomRight)
        glTexCoord2f(0.0,0.0);glVertex3f(*self.bottomLeft)
        glEnd()
        
        if self.textureGL:
            glDisable(GL_TEXTURE_2D)
        
    
    
        