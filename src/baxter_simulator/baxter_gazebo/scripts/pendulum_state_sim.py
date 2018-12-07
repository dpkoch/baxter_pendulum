#!/usr/bin/env python
from __future__ import print_function
import rospy
import numpy as np
from geometry_msgs.msg import PoseStamped
import tf
from tf.transformations import *

class PendulumStateSim:

    def __init__(self):
        self.gripper_home = np.array([0,0,0])
        self.listener = tf.TransformListener()
        self.pend_msg = PoseStamped()

        rospy.Subscriber('/robot/pendulum/pose/NWU', PoseStamped, self.pose_cb)

        self.pub = rospy.Publisher('/robot/pendulum/error_pose', PoseStamped, queue_size=1)

        rospy.loginfo("Init pendulum_state_sim node")

    def pose_cb(self, msg):
        try:
            pos_pend = np.array([msg.pose.position.x,
                                 msg.pose.position.y,
                                 msg.pose.position.z])

            quat_pend = np.array([msg.pose.orientation.x,
                                  msg.pose.orientation.y,
                                  msg.pose.orientation.z,
                                  msg.pose.orientation.w])

            pos_grip, _ = self.listener.lookupTransform('/world', '/left_gripper', rospy.Time(0))
            pos_grip = np.array(pos_grip)
            if np.array_equal(self.gripper_home, [0,0,0]):
                self.gripper_home = pos_grip

            pos_error = pos_grip - self.gripper_home

            xp = quaternion_matrix(quat_pend)[:3,0]
            theta = np.arctan2(-xp[0], -xp[2])  # angle on xz-plane
            phi = np.arctan2(-xp[1], -xp[2])    # angle on yz-plane

            p = self.pend_msg.pose.position
            o = self.pend_msg.pose.orientation
            p.x, p.y, _ = pos_error
            o.x, o.y = theta, phi

            self.pub.publish(self.pend_msg)

        except (tf.LookupException, tf.ConnectivityException, tf.ExtrapolationException):
            pass

if __name__ == '__main__':
    rospy.init_node("pendulum_state_sim", anonymous=True)
    aspd = PendulumStateSim()
    rate = rospy.Rate(60)  # Rate of main loop (Hz)

    while not rospy.is_shutdown():
        rospy.spin()