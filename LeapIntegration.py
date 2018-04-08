################################################################################
# Disclaimer: I do not own Leap Motion or any of it's technology stack or SDK.  
# Disclaimer: I do not own Vizard or any of the Worldviz IP.

# Use of this module in your project is subject to the terms of the Leap Motion SDK Agreement
# Use of this module in your project is also subject to the terms of Worldviz licensing.

# This Leap Integration Module for Vizard v5.8 and Leap Motion SDK 3.2.1 was written by Mark Brosche,
# Use of this module outside of the standard MIT License is not supported.

# This module is designed to populate a virtual environment with shape primitives that use Leap Motion
# tracking data to represent your hands in VR with the HTC Vive and SteamVR.  

# As of the latest update, hands are visualizations only and not for interactions.

################################################################################

import  Leap, sys, thread, time, viz, vizact, vizshape, viztask, steamvr, vizinfo, vizfx, vizmat, vizconnect

class LeapListener(Leap.Listener):
    OFFSET_SCALE = 1
    FINGER_WIDTH = 0.004
    JOINT_SIZE = 0.005
    storedLengthl =  0.1
    storedLengthr =  0.1
    initialized = False

    def on_init(self, controller):
        print "Initialized"

    def on_connect(self, controller):
        print "Connected"

    def on_disconnect(self, controller):
        # Note: not dispatched when running in a debugger.
        print "Disconnected"

    def on_exit(self, controller):
        print "Exited"
        
    def leap_to_world(self, leap_point, iBox):
        leap_point.z *= -.6255319; #right-hand to left-hand rule #must scale the z direction because the ibox is an elongated cuboid
        normalized = iBox.normalize_point(leap_point, False)
        normalized = normalized + Leap.Vector(-.6255319, 0.1755319, -.6255319); #recenter origin
        return normalized * .25; #scale

    def on_frame(self, controller):
        self.frame = self.controller.frame()
        if self.frame.hands.is_empty:
            self.hand_box.visible(viz.OFF)
            self.left_joints.visible(viz.OFF)
            self.right_joints.visible(viz.OFF)
            self.left_bones.visible(viz.OFF)
            self.right_bones.visible(viz.OFF)
        else:
            self.hand_box.visible(viz.ON)
            self.left_joints.visible(viz.ON)
            self.right_joints.visible(viz.ON)
            self.left_bones.visible(viz.ON)
            self.right_bones.visible(viz.ON)
#        if self.frame.is_valid and self.initialized:
        self.leftData()
        self.rightData()
        
 
    def leftData(self):
             frame = self.controller.frame()
             ibox = frame.interaction_box
             # Get hands
             hand = frame.hands.leftmost
             nextpos = self.leap_to_world(hand.palm_position, ibox)
             self.lhj[0].setPosition([nextpos.x * -1 * self.OFFSET_SCALE, nextpos.z * self.OFFSET_SCALE, nextpos.y * self.OFFSET_SCALE])
             # Get fingers
             for f in range(0,5):
                        finger = hand.fingers[f]
                        # Get bones
                        for b in range(0, 4):
                            bone = finger.bone(b)
                            nextpos = self.leap_to_world(bone.next_joint, ibox)
                            centerpos = self.leap_to_world(bone.center, ibox)
                            prevpos =  self.leap_to_world(bone.prev_joint, ibox)
                            length = bone.length 
                            num = 1 + b + (4*f)
                            self.lhj[num].setPosition([nextpos.x * -1 *self.OFFSET_SCALE,nextpos.z * self.OFFSET_SCALE, nextpos.y * self.OFFSET_SCALE])
                            if f is 1 and b is 0:
                                self.lhj[22].setPosition([prevpos.x * -1 * self.OFFSET_SCALE,prevpos.z * self.OFFSET_SCALE, prevpos.y * self.OFFSET_SCALE])
                            if f is 4 and b is 0:
                                self.lhj[21].setPosition([prevpos.x * -1 * self.OFFSET_SCALE,prevpos.z * self.OFFSET_SCALE, prevpos.y * self.OFFSET_SCALE])
#                            if self.left_segments[num-1] is not 0:
                            self.left_segments[num-1].setPosition([centerpos.x * -self.OFFSET_SCALE, centerpos.z * self.OFFSET_SCALE, centerpos.y * self.OFFSET_SCALE])
                            self.left_segments[num-1].lookAt(self.lhj[num].getPosition())
#                                if (abs( length - self.storedLengthl )) >  1:                            
#                                    scaleFactor = length / self.storedLengthl
#                                    self.left_segments[num-1].setScale([0, 0, scaleFactor])
#                                    self.storedLengthl = length
                    
            
    def rightData(self): 
            frame = self.controller.frame()
            ibox = frame.interaction_box
            hand = frame.hands.rightmost
            nextpos = self.leap_to_world(hand.palm_position, ibox)
            self.rhj[0].setPosition([nextpos.x * -1 * self.OFFSET_SCALE,nextpos.z * self.OFFSET_SCALE, nextpos.y * self.OFFSET_SCALE])
            # Get fingers
            for f in range(0,5):
                    finger = hand.fingers[f]
                    # Get bones
                    for b in range(0, 4):
                        bone = finger.bone(b)
                        nextpos = self.leap_to_world(bone.next_joint, ibox)
                        centerpos = self.leap_to_world(bone.center, ibox)
                        prevpos =  self.leap_to_world(bone.prev_joint, ibox)
                        length = bone.length * .001
                        num = 1 + b + (4*f)
                        self.rhj[num].setPosition([nextpos.x * -1 * self.OFFSET_SCALE,nextpos.z * self.OFFSET_SCALE, nextpos.y * self.OFFSET_SCALE])
                        if f is 1 and b is 0:
                            self.rhj[22].setPosition([prevpos.x * -1 * self.OFFSET_SCALE,prevpos.z * self.OFFSET_SCALE, prevpos.y * self.OFFSET_SCALE])
                        if f is 4 and b is 0:
                            self.rhj[21].setPosition([prevpos.x * -1 * self.OFFSET_SCALE,prevpos.z * self.OFFSET_SCALE, prevpos.y * self.OFFSET_SCALE])
#                        if self.right_segments[num-1] is not 0:
                        self.right_segments[num-1].setPosition([centerpos.x * -self.OFFSET_SCALE, centerpos.z * self.OFFSET_SCALE, centerpos.y * self.OFFSET_SCALE])
                        self.right_segments[num-1].lookAt(self.rhj[num].getPosition())
#                            if (abs( length - self.storedLengthr )) >  0.01:                            
#                                scaleFactor = length / self.storedLengthr
#                                self.right_segments[(1+(4*f)+b)].setScale([0, 0, scaleFactor])
#                                self.storedLengthr = length

    def startLeap(self, headset):
            # Create a listener and controller
            self.controller = Leap.Controller()
            self.controller.add_listener(self)
 # Have the listener receive events from the controller            
            self.controller.set_policy(Leap.Controller.POLICY_BACKGROUND_FRAMES)
            self.controller.set_policy(Leap.Controller.POLICY_OPTIMIZE_HMD)
            
            self.hand_box  = viz.addGroup()
            self.left_joints = viz.addGroup()
            self.right_joints  = viz.addGroup()
            self.left_bones  = viz.addGroup()
            self.right_bones  = viz.addGroup()
            self.leftyLink = viz.link(self.hand_box, self.left_joints)
            self.leftSegmentLink = viz.link(self.hand_box, self.left_bones)
            leftightyLink = viz.link(self.hand_box, self.right_joints)
            self.rightSegmentLink = viz.link(self.hand_box, self.right_bones)
            self.headlink = viz.link(headset, self.hand_box)
            self.headlink.preTrans([0,0,0.1143])

#            self.hand_box.setPosition(0, 2, .5)
            self.intbox = vizshape.addBox([.1,.1,.1])
            self.intbox.polyMode(viz.POLY_WIRE)
            self.intbox.emissive(1,0,1)
            self.intbox.setParent(self.hand_box)
            
        
            self.rhj = [] # right hand joints
            for i in range(23):
                if i is 0:
                    self.rhj.append(vizshape.addSphere(.01))
                else:
                    self.rhj.append(vizshape.addSphere(self.JOINT_SIZE))
                self.rhj[i].setParent(self.right_joints)
            
#            self.rhb = [] # right hand bones
#            for i in range(23):
#                if i < 4:
#                    self.rhb.append(vizshape.addSphere(.01))
#                else:
#                    self.rhb.append(vizshape.addCylinder(self.JOINT_SIZE))
#                self.rhb[i].setParent(self.right_bones)
#                              
            #right hand segments
#            self.rpalms = 0
            self.rthms = vizshape.addCylinder(0.01, self.FINGER_WIDTH, axis=vizshape.AXIS_Z)
            self.rthms.visible(viz.OFF)
            self.rthps = vizshape.addCylinder(0.03, self.FINGER_WIDTH, axis=vizshape.AXIS_Z)
            self.rthis  = vizshape.addCylinder(0.02, self.FINGER_WIDTH, axis=vizshape.AXIS_Z)
            self.rthds  = vizshape.addCylinder(0.01, self.FINGER_WIDTH, axis=vizshape.AXIS_Z)
            self.rinms  = vizshape.addCylinder(0.08, self.FINGER_WIDTH, axis=vizshape.AXIS_Z)
            self.rinps  = vizshape.addCylinder(0.03, self.FINGER_WIDTH, axis=vizshape.AXIS_Z)
            self.rinis  = vizshape.addCylinder(0.02, self.FINGER_WIDTH, axis=vizshape.AXIS_Z)
            self.rinds = vizshape.addCylinder(0.01, self.FINGER_WIDTH, axis=vizshape.AXIS_Z)
            self.rmips  = vizshape.addCylinder(0.01, self.FINGER_WIDTH, axis=vizshape.AXIS_Z)
            self.rmiis  = vizshape.addCylinder(0.01, self.FINGER_WIDTH, axis=vizshape.AXIS_Z)
            self.rmids  = vizshape.addCylinder(0.01, self.FINGER_WIDTH, axis=vizshape.AXIS_Z)
            self.rrips  = vizshape.addCylinder(0.01, self.FINGER_WIDTH, axis=vizshape.AXIS_Z)
            self.rriis  = vizshape.addCylinder(0.01, self.FINGER_WIDTH, axis=vizshape.AXIS_Z)
            self.rrids  = vizshape.addCylinder(0.01, self.FINGER_WIDTH, axis=vizshape.AXIS_Z)
            self.rpims  = vizshape.addCylinder(0.01, self.FINGER_WIDTH, axis=vizshape.AXIS_Z)
            self.rpips  = vizshape.addCylinder(0.01, self.FINGER_WIDTH, axis=vizshape.AXIS_Z)
            self.rpiis  = vizshape.addCylinder(0.01, self.FINGER_WIDTH, axis=vizshape.AXIS_Z)
            self.rpids  = vizshape.addCylinder(0.01, self.FINGER_WIDTH, axis=vizshape.AXIS_Z)
            self.rmims = vizshape.addCylinder(0.01, self.FINGER_WIDTH, axis=vizshape.AXIS_Z)
            self.rmims.visible(viz.OFF)
            self.rrims = vizshape.addCylinder(0.01, self.FINGER_WIDTH, axis=vizshape.AXIS_Z)
            self.rrims.visible(viz.OFF)
            self.rints = vizshape.addCylinder(0.01, self.FINGER_WIDTH, axis=vizshape.AXIS_Z)
            self.rints.visible(viz.OFF)
            self.rpits = vizshape.addCylinder(0.01, self.FINGER_WIDTH, axis=vizshape.AXIS_Z)
            self.rpits.visible(viz.OFF)
#            self.rpalms.setParent(self.right_bones)
#            self.rthms.setParent(self.right_bones)
            self.rthps.setParent(self.right_bones)
            self.rthis.setParent(self.right_bones)
            self.rthds.setParent(self.right_bones)
            self.rinms.setParent(self.right_bones)
            self.rinps.setParent(self.right_bones)
            self.rinis.setParent(self.right_bones)
            self.rinds.setParent(self.right_bones)
            self.rmips.setParent(self.right_bones)
            self.rmiis.setParent(self.right_bones)
            self.rmids.setParent(self.right_bones)
            self.rrips.setParent(self.right_bones)
            self.rriis.setParent(self.right_bones)
            self.rrids.setParent(self.right_bones)
            self.rpims.setParent(self.right_bones)
            self.rpips.setParent(self.right_bones)
            self.rpiis.setParent(self.right_bones)
            self.rpids.setParent(self.right_bones)
#            self.rmims.setParent(self.right_bones)
#            self.rrims.setParent(self.right_bones)
#            self.rints.setParent(self.right_bones)
#            self.rpits.setParent(self.right_bones)

            self.right_segments = [
                              self.rthms,      self.rthps,        self.rthis,       self.rthds, 
                              self.rinms,      self.rinps,         self.rinis,        self.rinds,      
                              self.rmims,     self.rmips,       self. rmiis,      self.rmids, 
                              self.rrims,        self.rrips,          self.rriis,        self.rrids, 
                              self.rpims,       self.rpips,         self.rpiis,       self.rpids,        
                              self.rints,         self.rpits  ]

            self.lhj = [] # left hand joints
            for i in range(23):
                if i is 0:
                    self.lhj.append(vizshape.addSphere(.01))
                else:
                    self.lhj.append(vizshape.addSphere(self.JOINT_SIZE))
                self.lhj[i].setParent(self.left_joints)
                              
            #left hand segments
#            self.lpalms = 0
            self.lthms = vizshape.addCylinder(.01, self.FINGER_WIDTH, axis=vizshape.AXIS_Z)
            self.lthms.visible(viz.OFF)
            self.lthps = vizshape.addCylinder(.01, self.FINGER_WIDTH, axis=vizshape.AXIS_Z)
            self.lthis  = vizshape.addCylinder(.01, self.FINGER_WIDTH, axis=vizshape.AXIS_Z)
            self.lthds  = vizshape.addCylinder(.01, self.FINGER_WIDTH, axis=vizshape.AXIS_Z)
            self.linms  = vizshape.addCylinder(.01, self.FINGER_WIDTH, axis=vizshape.AXIS_Z)
            self.linps  = vizshape.addCylinder(.01, self.FINGER_WIDTH, axis=vizshape.AXIS_Z)
            self.linis  = vizshape.addCylinder(.01, self.FINGER_WIDTH, axis=vizshape.AXIS_Z)
            self.linds = vizshape.addCylinder(.01, self.FINGER_WIDTH, axis=vizshape.AXIS_Z)
            self.lmips  = vizshape.addCylinder(.01, self.FINGER_WIDTH, axis=vizshape.AXIS_Z)
            self.lmiis  = vizshape.addCylinder(.01, self.FINGER_WIDTH, axis=vizshape.AXIS_Z)
            self.lmids  = vizshape.addCylinder(.01, self.FINGER_WIDTH, axis=vizshape.AXIS_Z)
            self.lrips  = vizshape.addCylinder(.01, self.FINGER_WIDTH, axis=vizshape.AXIS_Z)
            self.lriis  = vizshape.addCylinder(.01, self.FINGER_WIDTH, axis=vizshape.AXIS_Z)
            self.lrids  = vizshape.addCylinder(.01, self.FINGER_WIDTH, axis=vizshape.AXIS_Z)
            self.lpims  = vizshape.addCylinder(.01, self.FINGER_WIDTH, axis=vizshape.AXIS_Z)
            self.lpips  = vizshape.addCylinder(.01, self.FINGER_WIDTH, axis=vizshape.AXIS_Z)
            self.lpiis  = vizshape.addCylinder(.01, self.FINGER_WIDTH, axis=vizshape.AXIS_Z)
            self.lpids  = vizshape.addCylinder(.01, self.FINGER_WIDTH, axis=vizshape.AXIS_Z)
            self.lmims = vizshape.addCylinder(.01, self.FINGER_WIDTH, axis=vizshape.AXIS_Z)
            self.lmims.visible(viz.OFF)
            self.lrims = vizshape.addCylinder(.01, self.FINGER_WIDTH, axis=vizshape.AXIS_Z)
            self.lrims.visible(viz.OFF)
            self.lpits =vizshape.addCylinder(.01, self.FINGER_WIDTH, axis=vizshape.AXIS_Z)
            self.lpits.visible(viz.OFF)
            self.lints = vizshape.addCylinder(.01, self.FINGER_WIDTH, axis=vizshape.AXIS_Z)
            self.lints.visible(viz.OFF)
#            self.lpalms.setParent(self.left_bones)
            self.lthms.setParent(self.left_bones)
            self.lthps.setParent(self.left_bones)
            self.lthis.setParent(self.left_bones)
            self.lthds.setParent(self.left_bones)
            self.linms.setParent(self.left_bones)
            self.linps.setParent(self.left_bones)
            self.linis.setParent(self.left_bones)
            self.linds.setParent(self.left_bones)
            self.lmips.setParent(self.left_bones)
            self.lmiis.setParent(self.left_bones)
            self.lmids.setParent(self.left_bones)
            self.lrips.setParent(self.left_bones)
            self.lriis.setParent(self.left_bones)
            self.lrids.setParent(self.left_bones)
            self.lpims.setParent(self.left_bones)
            self.lpips.setParent(self.left_bones)
            self.lpiis.setParent(self.left_bones)
            self.lpids.setParent(self.left_bones)

            self.left_segments = [
                             self.lthms,    self.lthps,      self.lthis,       self.lthds, 
                             self.linms,     self.linps,        self.linis,       self.linds,      
                             self.lmims,    self.lmips,      self.lmiis,     self.lmids, 
                             self.lrims,      self.lrips,         self.lriis,       self.lrids, 
                             self.lpims,      self.lpips,        self.lpiis,      self.lpids,        
                            self.lpits,        self.lints   ]    
                            
            self.right_bones.color(viz.WHITE)
            self.left_bones.color(viz.WHITE)
            self.right_joints.color(viz.CYAN)
            self.left_joints.color(viz.CYAN)
            self.initialized = True
            print 'initialized the hands'

def main():
    # Initialize window
    viz.setMultiSample(8)
    viz.go()

    # Setup SteamVR HMD
    hmd = steamvr.HMD()
    if not hmd.getSensor():
        sys.exit('SteamVR HMD not detected')

    # Setup navigation node and link to main view
    navigationNode = viz.addGroup()
    viewLink = viz.link(navigationNode, viz.MainView)
    viewLink.preMultLinkable(hmd.getSensor())

    # Load environment
    gallery = vizfx.addChild('lab.osgb')
    gallery.hint(viz.OPTIMIZE_INTERSECT_HINT)
    gallery.disable(viz.SHADOW_CASTING)
    origin = vizshape.addAxes()
    origin.setPosition([0,0,0])

    #Create skylight
    viz.MainView.getHeadLight().disable()
    sky_light = viz.addDirectionalLight(euler=(0,90,0), color=viz.WHITE)
    sky_light.setShadowMode(viz.SHADOW_DEPTH_MAP)
    
    #Start the Leap Motion!
    handGenerator = LeapListener()
    handGenerator.startLeap(hmd.getSensor())
    
    # Add controllers
    for controller in steamvr.getControllerList():

        # Create model for controller
        controller.model = controller.addModel(parent=navigationNode)
        controller.model.disable(viz.INTERSECTION)
        viz.link(controller, controller.model)

if __name__ == "__main__":
    main()
