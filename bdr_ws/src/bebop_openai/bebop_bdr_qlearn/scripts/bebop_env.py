import numpy as np
import rospy
import time

import robot_ros_env

from std_msgs.msg import Float64
from sensor_msgs.msg import JointState
from sensor_msgs.msg import Image
from sensor_msgs.msg import LaserScan
from sensor_msgs.msg import PointCloud2
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Twist
from sensor_msgs.msg import Range
from sensor_msgs.msg import Imu
from geometry_msgs.msg import Pose
from std_msgs.msg import Empty

import cv2
from cv_bridge import CvBridge, CvBridgeError
from gym import spaces
import pandas as pd

class Bebop2Env(robot_ros_env.RobotRosEnv):

    def __init__(self):
	    self.camera_image_raw = None
        self.lateral = 0
        self.speed = 0
        self.yaw = 0

        # Define action and observation space
        self.action_space = spaces.Box(np.array([-1, 0, -1]), np.array([1, 0.5, 1]), dtype=np.float32) #yaw, speed, lateral
        self.observation_space = np.zeros(shape=(100,100))

        self.num_bins = 10
        self.angular_z_bins = pd.cut([-1, 1], bins=num_bins, retbins=True)[1][1:-1]
        self.linear_x_bins  = pd.cut([ 0, 1], bins=num_bins, retbins=True)[1][1:-1]
        self.linear_y_bins  = pd.cut([-1, 1], bins=num_bins, retbins=True)[1][1:-1]

        self.move_low = -1.0
        self.speed_low = 0.0
        self.high = 1.0

        # Launch the init function of the Parent Class robot_gazebo_env.RobotGazeboEnv
        super(Bebop2Env, self).__init__()

        # Start all the ROS related components
        self._image_sub = rospy.Subscriber("/bebop/image_raw", Image, self._camera_image_raw_callback)
        self._image_pub = rospy.Publisher("bebop/filtered", Image, queue_size=1)
        self._cmd_vel_pub = rospy.Publisher('/bebop/cmd_vel', Twist, queue_size=1)
        self._takeoff_pub = rospy.Publisher('/bebop/takeoff', Empty, queue_size=1)
        self._land_pub = rospy.Publisher('/bebop/land', Empty, queue_size=1)

        self._check_all_sensors_ready()
        self._check_all_publishers_ready()
        rospy.logwarn("Bebop2 Environment initialized")

    def _check_all_sensors_ready(self):
        self._check_camera_image_raw_ready()
        
    def _check_camera_image_raw_ready(self):
        self.camera_image_raw = None
        rospy.logerr("Waiting for /bebop/image_raw to be ready...")
        while self.camera_image_raw is None and not rospy.is_shutdown():
            try:
                self.camera_image_raw = rospy.wait_for_message("/bebop/image_raw", Image, timeout=5.0)
                rospy.logdebug("/bebop/image_raw ready =>")
            except:
                rospy.logerr("/bebop/image_raw not ready yet, retrying...")
        return self.camera_image_raw
        
    def _camera_image_raw_callback(self, data):
        bridge = CvBridge()
        img = bridge.imgmsg_to_cv2(data, "bgr8")

        # filter by red
        hls  = cv2.cvtColor(self.image, cv2.COLOR_RGB2HLS)
        lower = np.array([0,   100, 100], dtype=np.uint8)
        upper = np.array([125, 200, 200], dtype=np.uint8)
        filtered = cv2.inRange(hls, lower, upper)

        # convert to grayscale
        gray = cv2.cvtColor(filtered, cv2.COLOR_HLS2GRAY)
        scaled = cv2.resize(gray, None, fx=0.25, fy=0.25)    
        print(scaled.shape())

        self.camera_image_raw = scaled
        self._image_pub.publish(bridge.cv2_to_imgmsg(scaled))
    
    def _check_all_publishers_ready(self):
        self._check_cmd_vel_pub_connection()
        self._check_takeoff_pub_connection()
        self._check_land_pub_connection()

    def _check_cmd_vel_pub_connection(self):
        rate = rospy.Rate(10)
        while self._cmd_vel_pub.get_num_connections() == 0 and not rospy.is_shutdown():
            rospy.logerr("/bebop/cmd_vel not ready yet, retrying...")
            try:
                rate.sleep()
            except rospy.ROSInterruptException:
                pass
        rospy.logdebug("/bebop/cmd_vel publisher ready =>")
        
    def _check_takeoff_pub_connection(self):
        rate = rospy.Rate(10)
        while self._takeoff_pub.get_num_connections() == 0 and not rospy.is_shutdown():
            rospy.logerr("/bebop/takeoff not ready yet, retrying...")
            try:
                rate.sleep()
            except rospy.ROSInterruptException:
                pass
        rospy.logdebug("/bebop/takeoff publisher ready =>")
        
    def _check_land_pub_connection(self):
        rate = rospy.Rate(10)
        while self._land_pub.get_num_connections() == 0 and not rospy.is_shutdown():
            rospy.logerr("/bebop/land not ready yet, retrying...")
            try:
                rate.sleep()
            except rospy.ROSInterruptException:
                pass
        rospy.logdebug("/bebop/land publisher ready =>")

    def _compute_reward(self, observations, done):
        raise NotImplementedError()

    def _set_action(self, action):
        raise NotImplementedError()

    def _get_obs(self):
        raise NotImplementedError()

    def _is_done(self, observations):
        raise NotImplementedError()
        
    def takeoff(self):
        takeoff_cmd = Empty()

        self._check_takeoff_pub_connection()  
        self._takeoff_pub.publish(takeoff_cmd)
        self.wait_time_for_execute_movement()
        
    def land(self):
        land_cmd = Empty()
        
        self._check_land_pub_connection()
        self._land_pub.publish(land_cmd)
        self.wait_time_for_execute_movement()
        
    def get_bin_value(self, bins, idx, low):
        if idx == 0:
            return np.average([low, bins[idx]])
        elif idx == 9:
            return np.average([bins[idx-1], self.high])
        else:
            return np.average([bins[idx], bins[idx-1]]) 

    def move(self, x):
        self.yaw = self.get_bin_value(self.angular_z_bins, x[0], self.move_low)
        self.lateral = self.get_bin_value(self.linear_y_bins, x[1], self.move_low)
        self.speed = self.get_bin_value(self.linear_x_bins, x[2], self.speed_low)
        
        yaw_clean = float("{0:.1f}".format(self.yaw))
        lateral_clean = float("{0:.1f}".format(self.lateral))
        speed_clean = float("{0:.1f}".format(self.speed))

        print("Action Taken: " + str((yaw_clean, lateral_clean, speed_clean)) + "\n")

        velocity_cmd = Twist()
        velocity_cmd.angular.z = self.yaw
        velocity_cmd.linear.x  = self.speed
        velocity_cmd.linear.y  = self.lateral

        self._check_cmd_vel_pub_connection()
        #self._cmd_vel_pub.publish(velocity_cmd)
        self.wait_time_for_execute_movement()

                                        
    def wait_time_for_execute_movement(self):
        time.sleep(1.0)
    
    def get_camera_image_raw(self):
        return self.camera_image_raw