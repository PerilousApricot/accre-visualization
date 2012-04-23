"""
Timeline - 
    handles animating state

Created by Andrew Melo <andrew.melo@gmail.com> on Apr 22, 2012
"""

from math import sin, cos

class Timeline:
    def __init__(self, name):
        self.name     = name
        self.next     = None
        self.tweens   = []
        self.duration = 10 * 1000 # 10 sec
        self._isDone  = False
    
    def start(self,currentTime):
        self.startTime = currentTime
        self._isDone   = False
        for tween in self.tweens:
            tween.start()
    
    def update(self, currentTime):
        alpha = float( float(currentTime - self.startTime) / float(self.duration) )
        if alpha > 1.0:
            alpha = 1.0
            self._isDone = True
            print "Timeline done: %s" % self.name
        for tween in self.tweens:
            tween.update( alpha )
    
    def getNext(self):
        return self.next
    
    def setNext(self, _next):
        self.next =_next
        
    def isDone(self):
        return self._isDone

class Tween:
    """
    interpolates between values in realtime
    """
    def start(self):
        pass
    def update(self, alpha):
        pass
    def lerpVectors(self, src, dest, alpha):
        return ( alpha * dest[0] + (1 - alpha) * src[0],
                 alpha * dest[1] + (1 - alpha) * src[1],
                 alpha * dest[2] + (1 - alpha) * src[2])
        
class MoveCameraTween(Tween):
    def __init__(self, camera, pos, lookat, up, arrivalAlpha = 1.0):
        self.camera   = camera
        self.pos_2    = pos
        self.lookat_2 = lookat
        self.up_2     = up
        self.arrivalAlpha = arrivalAlpha
    
    def start(self):
        self.pos_1    = self.camera.pos[:]
        self.lookat_1 = self.camera.lookat[:]
        self.up_1     = self.camera.up[:]
    
    def update(self, alpha):
        alpha = min( 1.0, alpha/self.arrivalAlpha )
        self.camera.pos = self.lerpVectors( self.pos_1, self.pos_2, alpha)
        self.camera.lookat = self.lerpVectors( self.lookat_1, self.lookat_2, alpha)
        self.camera.up = self.lerpVectors( self.up_1, self.up_2, alpha)
        
class RotateCameraTween(Tween):
    def __init__(self, camera, init_lat, init_long, radius, rotations, look, up):
        self.camera = camera
        self.init_lat = init_lat
        self.init_long = init_long
        self.radius = radius
        self.rotations = rotations
        self.look = look
        self.up = up
        
    def toCartesian(self, lat, longitude, height):
        return toCartesian( lat, longitude, height)
        
    def update(self, alpha):
        self.camera.pos = self.toCartesian(self.init_lat, 
                                           (self.init_long + 360 * alpha * self.rotations),
                                            self.radius)
        self.camera.look = self.look[:]
        self.camera.up = self.up[:]
        
def toCartesian(lat, longitude, height):
        # the top/bottom 15 degrees are trimmed from the map
        latrad  = lat * 3.14 / 180.0 # * 90.0 / 75.0
        longituderad = longitude * 3.14 / 180.0
        retval = (height * cos(latrad) * cos(longituderad),
                  height * sin(latrad),
                 -1 * height * cos(latrad) * sin(longituderad),
                  )
#        print "Coordinates %.1f %.1f %.1f for %.1f %.1f %.1f" % \
#            (retval[0],retval[1],retval[2],lat,longitude, height)
        return retval 

class HideTween(Tween):
    def __init__(self, children):
        self.children = children
    def start(self):
        for child in self.children:
            child.setInvisible()
            
class ShowTween(Tween):
    def __init__(self, children):
        self.children = children
    def start(self):
        for child in self.children:
            child.setVisible()