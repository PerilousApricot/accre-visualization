#!/usr/bin/env python2.6

# client

import zmq
import time
import clutter
import BezeledContainer
import threading

class ACCREDashboard:
    def networkingThread(self):
        context = zmq.Context()
        zsock   = context.socket(zmq.SUB)
        zsock.connect("tcp://se2.accre.vanderbilt.edu:9898")
        zsock.setsockopt(zmq.SUBSCRIBE, "")

        while True: #read everything! Bomb with done.
            try:
                trans = zsock.recv_json( )
                with self.mesageLock:
                    self.messageQueue.append( trans )
            except zmq.ZMQError, e:
                # slowwwww dowwwwnnn
                time.sleep(0.01)
                pass
    
    def __init__(self):
        
        color_grey = clutter.Color(127,127,127,255)
        color_lightgrey = clutter.Color(192,192,192,255)
        color_darkgrey  = clutter.Color(92,92,92,255)
        color_green = clutter.Color(20,166,42,255)
        color_black = clutter.Color(0,0,0,255)
        
        self.messageQueue  = []
        self.messageLock   = threading.Lock()
        self.messageThread = threading.Thread( group = None, target = self.networkingThread, args=(self, )) 
        
        self.stage = clutter.Stage()
        self.stage.set_user_resizable( True )
        self.stage.set_color( color_darkgrey )
        # we're looking at 16:9 ratio
        self.stage.set_size( 800, 450 )

        
        # make callbacks
        self.stage.connect('key-press-event', self.parseKeyPress)
        #self.stage.connect('allocation-changed', self.handleResize)
        self.stage.connect('destroy', clutter.main_quit)
        
        self.globalContainer = BezeledContainer.BezeledRectangle()
        self.globalContainer.set_position(0,0)
        self.globalContainer.set_size(800,450)
        self.stage.add( self.globalContainer )
        
        self.leftSide = BezeledContainer.BezeledRectangle()
        self.leftSide.set_size(408,442)
        self.globalContainer.add(self.leftSide)
        
        self.rightSide = BezeledContainer.BezeledRectangle()
        self.rightSide.set_size(380,442)
        self.globalContainer.add(self.rightSide)
        
        self.MonitorPane = BezeledContainer.BezeledRectangle()
        self.MonitorPane.set_size(400,388)
        self.MonitorPane._color = [0,0,0]
        self.leftSide.add(self.MonitorPane)
        
        # Same for stop button.
        self.stopBtn = clutter.Rectangle() 
        self.stopBtn.set_color(clutter.Color(255,0,0, 255))
        self.stopBtn.set_size(50, 30) 
        self.stopBtn.set_position(218, 34) 
        self.stage.add(self.stopBtn) 

        StopTxt = clutter.Label() 
        StopTxt.set_text("Error") 
        StopTxt.set_font_name("Mono 32")
        StopTxt.set_color(clutter.color_parse('Black'))
        topLeftContraint = clutter.Constraint( self.MonitorPane, clutter.CLUTTER_BIND_X, 0)
        StopTxt.add_constraint( topLeftConstraint )
        self.stage.add(StopTxt) 
        
        self.MonitorDesc = BezeledContainer.BezeledRectangle()
        self.MonitorDesc.set_size(400,50)
        self.leftSide.add(self.MonitorDesc)
        
#        self.labelGroup = clutter.Group()
#        self.capLabel = clutter.Text()
#        self.capLabel.set_text("Capacity")
#        self.capLabel.set_color( color_black )
#        self.capLabel.set_font_name("Mono 16")
#        self.labelGroup.add( self.capLabel )
#        self.globalLabel = clutter.Text()
#        self.globalLabel.set_text("Global")
#        self.globalLabel.set_color( color_black )
#        self.globalLabel.set_font_name("Mono 16")
#        self.labelGroup.add( self.globalLabel )
#        self.rightSide.add( self.labelGroup )
        
        self.subsystemLabel = clutter.Text()
        self.subsystemLabel.set_text("ACCRE Status")
        self.subsystemLabel.set_color( color_black )
        self.subsystemLabel.set_font_name("Helvetica Bold Italic 32")
        self.MonitorDesc.add( self.subsystemLabel )
        
        
        self.stage.show_all()
        clutter.main()
        print "I made it?"
        return
        
        self.subContainer = BezeledContainer.BezeledRectangle()
        #self.globalContainer.add( self.subContainer )
        
        # Add blocks
        self.subsystemGroup = clutter.Group()
        self.subsystemGroup.set_position(12.5,12.5)
        self.stage.add( self.subsystemGroup )
        
        self.subsystemContainer = BezeledContainer.BezeledRectangle()
        #self.subsystemContainer.set_color( color_green)     
        self.subsystemContainer.set_position(0,0)
        #self.subsystemContainer.set_size(350,375)
        # changed from subsystemGroup
        self.stage.add( self.subsystemContainer )
        
        self.subsystemLabelContainer = clutter.Rectangle()
        self.subsystemLabelContainer.set_color( color_grey )     
        self.subsystemLabelContainer.set_position(0, 375)
        self.subsystemLabelContainer.set_size(350,50)
        self.subsystemGroup.add( self.subsystemLabelContainer )   
        
        self.subsystemLabel = clutter.Text()
        self.subsystemLabel.set_text("ACCRE Status")
        self.subsystemLabel.set_color( color_green )
        self.subsystemLabel.set_font_name("Mono 32")
        #(label_width, label_height) = self.label.get_size()
        self.subsystemLabel.set_position(0,375)
        self.subContainer.add( self.subsystemLabel )
        
#        self.label2 = clutter.Text()
#        self.label2.set_text("Say the magic word")
#        self.label2.set_color( color_green )
#        self.label2.set_font_name("Mono 32")
#        self.label.set_position(0,0)
        
        # animate it
#        self.timeline = clutter.Timeline(500)
#        labelalpha = clutter.Alpha(self.timeline, clutter.EASE_OUT_SINE)
#        #make some opacity behaviours that we will apply to the labels
#        self.hideBehaviour = clutter.BehaviourOpacity(255,0x00,labelalpha)
#        self.showBehaviour = clutter.BehaviourOpacity(0x00,255,labelalpha)
#        #add the items to the stage
#        self.stage.add(self.label2)
#        self.stage.add(self.label)
#        #show all stage items and enter the clutter main loop
#        self.swapLabels()

        
    def parseKeyPress(self,actor, event):
        #do stuff when the user presses a key
        #it would be awesome if I could find some documentation regarding clutter.keysyms
        if event.keyval in [clutter.keysyms.q, clutter.keysyms.Escape]:
            #if the user pressed "q" quit the test
            clutter.main_quit()
        elif event.keyval == clutter.keysyms.s:
            #if the user pressed "s" swap the labels
            self.swapLabels()
    
    def handleResize(self, stage, box, foo):
        print "Resized to (%s,%s)-(%s,%s)" % (box.x1, box.y1, box.x2, box.y2)
        widthRatio  = float(800.0) / box.x2
        heightRatio = float(450.0) / box.y2
        targetRatio = 1.0 / min(widthRatio, heightRatio)
        #print "  ratio is %s %s %s" % (widthRatio, heightRatio, targetRatio)
        #self.stage.set_scale( targetRatio, targetRatio )
        
    
    def swapLabels(self):
        pass
        #which label is at full opacity?, like the highlander, there can be only one
#        if(self.label.get_opacity()>=1 ):
#            showing = self.label
#            hidden = self.label2
#        else:
#            showing = self.label2
#            hidden = self.label
#        #detach all objects from the behaviors
#        self.hideBehaviour.remove_all()
#        self.showBehaviour.remove_all()
#        #apply the behaviors to the labels
#        self.hideBehaviour.apply(showing)
#        self.showBehaviour.apply(hidden)
#        #behaviours do nothing if their timelines are not running
#        self.timeline.start()


def idleFunc():
    print "in here!"

if __name__=="__main__":
    test = ACCREDashboard()
           
