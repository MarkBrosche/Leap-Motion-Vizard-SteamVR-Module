################################################################################
# Disclaimer: I do not own Leap Motion or any of it's technology stack or SDK.  
# Disclaimer: I do not own Vizard or any Worldviz IP.

# Use of this module in your project is subject to the terms of the Leap Motion SDK Agreement
# Use of this module in your project is also subject to the terms of Worldviz licensing.

# This Leap Integration Module for Vizard v5.8 and Leap Motion SDK 3.2.1 was written by Mark Brosche,
# Use of this module outside of the standard MIT License is not supported.

# This module is designed to populate a virtual environment with shape primitives that use Leap Motion
# tracking data to represent your hands in VR with the HTC Vive and SteamVR.  

# As of the latest update, hands are visualizations only and not for interactions.

################################################################################

import  Leap, sys, thread, time, viz, vizshape, steamvr, vizfx

class LeapListener(Leap.Listener):
    FINGER_WIDTH = 0.006
    JOINT_SIZE = 0.008
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
        self.leftData()
        self.rightData()
            
    def leftData(self):
             frame = self.controller.frame()
             ibox = frame.interaction_box
             # Get hands
             hand = frame.hands.leftmost
             nextpos = self.leap_to_world(hand.palm_position, ibox)
             self.lhj[0].setPosition([nextpos.x * -1 , nextpos.z , nextpos.y ])
             # Get fingers
             for f in range(0,5):
                finger = hand.fingers[f]
                # Get bones
                for b in range(0, 4):
                    bone = finger.bone(b)
                    # forward knuckle
                    nextpos = self.leap_to_world(bone.next_joint, ibox)
                    # bone center
                    centerpos = self.leap_to_world(bone.center, ibox)
                    # previous knuckle
                    prevpos =  self.leap_to_world(bone.prev_joint, ibox)
                    length = bone.length 
                    num = 1 + b + (4*f)
                    self.lhj[num].setPosition([nextpos.x * -1,nextpos.z , nextpos.y ])
                    if f is 1 and b is 0:
                        self.lhj[22].setPosition([prevpos.x * -1,prevpos.z , prevpos.y ])
                    if f is 4 and b is 0:
                        self.lhj[21].setPosition([prevpos.x * -1,prevpos.z , prevpos.y ])
                    self.lhb[num-1].setPosition([centerpos.x * -1, centerpos.z , centerpos.y ])
                    self.lhb[num-1].lookAt(self.lhj[num].getPosition())
                    scaleFactor = length * 0.001
                    self.lhb[num-1].setScale(1, 1, scaleFactor)

    def rightData(self): 
            frame = self.controller.frame()
            ibox = frame.interaction_box
            hand = frame.hands.rightmost
            nextpos = self.leap_to_world(hand.palm_position, ibox)
            self.rhj[0].setPosition([nextpos.x * -1, nextpos.z, nextpos.y ])
            # Get fingers
            for f in range(0,5):
                finger = hand.fingers[f]
                # Get bones
                for b in range(0, 4):
                    bone = finger.bone(b)
                    # forward knuckle (away from wrist)
                    nextpos = self.leap_to_world(bone.next_joint, ibox)
                    # bone center
                    centerpos = self.leap_to_world(bone.center, ibox)
                    # previous knuckle (toward wrist)
                    prevpos =  self.leap_to_world(bone.prev_joint, ibox)
                    length = bone.length
                    num = 1 + b + (4*f)
                    self.rhj[num].setPosition([nextpos.x * -1, nextpos.z , nextpos.y ])
                    if f is 1 and b is 0:
                        self.rhj[22].setPosition([prevpos.x * -1, prevpos.z , prevpos.y ])
                    if f is 4 and b is 0:
                        self.rhj[21].setPosition([prevpos.x * -1, prevpos.z , prevpos.y ])
                    self.rhb[num-1].setPosition([centerpos.x * -1, centerpos.z, centerpos.y ])
                    self.rhb[num-1].lookAt(self.rhj[num].getPosition())                           
                    scaleFactor = length * 0.001
                    self.rhb[num-1].setScale([1, 1, scaleFactor])

    def startLeap(self, headset):
            # Create a listener and controller.
            self.controller = Leap.Controller()
            self.controller.add_listener(self)
            
            # Set controller policies for VR.         
            self.controller.set_policy(Leap.Controller.POLICY_BACKGROUND_FRAMES)
            self.controller.set_policy(Leap.Controller.POLICY_OPTIMIZE_HMD)
            
            # Set up relationships for the hands, joints, bones to the head.
            self.hand_box  = viz.addGroup()
            
            self.left_joints = viz.addGroup()
            self.left_bones  = viz.addGroup()
            self.ljLink = viz.link(self.hand_box, self.left_joints)
            self.lbLink = viz.link(self.hand_box, self.left_bones)
            
            self.right_joints  = viz.addGroup()
            self.right_bones  = viz.addGroup()
            self.rjLink = viz.link(self.hand_box, self.right_joints)
            self.rbLink = viz.link(self.hand_box, self.right_bones)
            
            self.headlink = viz.link(headset, self.hand_box)
            self.headlink.preTrans([0,0,0.1143])
           
            self.rhj = [] # right hand joints (knuckles)
            for i in range(23):
                if i is 0:
                    self.rhj.append(vizshape.addSphere(.015))
                else:
                    self.rhj.append(vizshape.addSphere(self.JOINT_SIZE))
                self.rhj[i].setParent(self.right_joints)
            
            self.rhb = [] # right hand bones
            for i in range(21):
                if (i == 12) or (i == 8) or (i >= 20) :
                    self.rhb.append(vizshape.addCube(.01))
                    self.rhb[i].visible(viz.OFF)
                else:
                    self.rhb.append(vizshape.addCylinder(1.0, self.FINGER_WIDTH, axis=vizshape.AXIS_Z))
                self.rhb[i].setParent(self.right_bones)

            self.lhj = [] # left hand joints (knuckles)
            for i in range(23):
                if i is 0:
                    self.lhj.append(vizshape.addSphere(.015))
                else:
                    self.lhj.append(vizshape.addSphere(self.JOINT_SIZE))
                self.lhj[i].setParent(self.left_joints)
                              
            self.lhb = [] # left hand bones
            for i in range(21):
                if  (i == 12) or (i == 8) or (i >= 20) :
                    self.lhb.append(vizshape.addCube(0.01))
                    self.lhb[i].visible(viz.OFF)
                else:
                    self.lhb.append(vizshape.addCylinder(1.0, self.FINGER_WIDTH, axis=vizshape.AXIS_Z))
                self.lhb[i].setParent(self.left_bones)
                            
            self.right_bones.color(viz.WHITE)
            self.left_bones.color(viz.WHITE)
            self.right_joints.color(viz.AZURE)
            self.left_joints.color(viz.AZURE)
            
            self.initialized = True      
            print 'Initialized the Hands!'

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
    gallery = vizfx.addChild('gallery.osgb')
    gallery.hint(viz.OPTIMIZE_INTERSECT_HINT)
    gallery.disable(viz.SHADOW_CASTING)

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
