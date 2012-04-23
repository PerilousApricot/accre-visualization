"""
TexturedGlobe - 
    Globe of the earth!

Created by Andrew Melo <andrew.melo@gmail.com> on Apr 22, 2012
"""

try:
    import Image
except ImportError:
    from PIL import Image
    
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from math import sin,cos
import Timeline

from VisibleObject import VisibleObject

OpenGL.FULL_LOGGING = True

class TexturedGlobe( VisibleObject ):
    textureGL     = None
    def __init__(self, pos = None):
        VisibleObject.__init__( self, pos )
        print "nashville is at %s %s %s" % self.toCartesian(36.1658, -86.7844,999)
        if not TexturedGlobe.textureGL:
            im = Image.open("world.jpg")
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
            # return the ID for use
            TexturedGlobe.textureGL = ID
        
    def toCartesian(self, latitude, longitude, height):
        return Timeline.toCartesian(latitude, longitude, height)

    def render(self):
        # texture-mode setup, was global in original
        glEnable(GL_TEXTURE_2D)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)
        # re-select our texture, could use other generated textures
        # if we had generated them earlier...
        glPushMatrix()
        glRotatef(-90.0,1,0,0)
        
        # the sphere need to rotate a bit forward to lne up coordinate
        # systems
        #glPushMatrix()
        glRotatef(90.0,0,0,1)
        glBindTexture(GL_TEXTURE_2D, TexturedGlobe.textureGL)
        quad = gluNewQuadric()
        gluQuadricNormals(quad, GLU_SMOOTH)
        gluQuadricTexture(quad, GL_TRUE)
        gluQuadricOrientation(quad, GLU_OUTSIDE)
        gluSphere(quad,1000,1000,1000)
        glutWireSphere( 1010 ,40,40)
                                            
        #glPopMatrix()
        glDisable(GL_TEXTURE_2D)
        glPopMatrix()
        
        glColor3f(1,0,0)
        glBegin(GL_LINES)
        glVertex3f(0.0,0.0,0.0)
        glVertex3f(* self.toCartesian( 0,0,1100 ))
        glColor3f(0,1,0)
        glVertex3f(0.0,0.0,0.0)
        glVertex3f(* self.toCartesian( 90,0,1100 ))
        glColor3f(0,0,1)
        glVertex3f(0.0,0.0,0.0)
        glVertex3f(* self.toCartesian( 0,90,1100 ))
        glColor3f(1,1,1)
        # cern
        #46.2342 N, 6.0528 E
        glVertex3f(0.0,0.0,0.0)
        glVertex3f(* self.toCartesian( 46.2352, 6.0528, 1100 ))
        glVertex3f(0.0,0.0,0.0)
        glVertex3f(* self.toCartesian( 36.1658, -86.67, 1100 ))
        glEnd()
        #glPopMatrix()

        

        #glEnable(GL_LIGHTING);