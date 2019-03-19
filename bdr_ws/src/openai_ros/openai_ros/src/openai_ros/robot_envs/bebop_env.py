import numpy
import rospy
import time
from openai_ros import robot_gazebo_env
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

class Bebop2Env(robot_gazebo_env.RobotGazeboEnv):

    def __init__(self):
        """
        Initializes a new Bebop2Env environment.
        
        Sensor Topic List:
        * /bebop/camera/image_raw: raw image topic
        
        Actuators Topic List: 
        * /bebop/cmd_vel: publish velocity commands
        * /bebop/takeoff: publish a takeoff command
        * /bebop/land: publish a land command
        """

        rospy.logdebug("Start Bebop2Env Init...")
        
        # Internal Vars
        self.controllers_list = []

        # Namespace
        self.robot_name_space = ""

        # Launch the init function of the Parent Class robot_gazebo_env.RobotGazeboEnv
        super(Bebop2Env, self).__init__(controllers_list=self.controllers_list,
                                            robot_name_space=self.robot_name_space,
                                            reset_controls=False,
                                            start_init_physics_parameters=False,
                                            reset_world_or_sim="WORLD")

        self.gazebo.unpauseSim()
        #self.controllers_object.reset_controllers()
        self._check_all_sensors_ready()

        # Start all the ROS related Subscribers and publishers
        self._image_sub = rospy.Subscriber("/bebop/image_raw", Image, self._camera_image_raw_callback)
        self._cmd_vel_pub = rospy.Publisher('/bebop/cmd_vel', Twist, queue_size=1)
        self._takeoff_pub = rospy.Publisher('/bebop/takeoff', Empty, queue_size=1)
        self._land_pub = rospy.Publisher('/bebop/land', Empty, queue_size=1)

        self._check_all_publishers_ready()
        self.gazebo.pauseSim()
        
        rospy.logdebug("Finished Bebop2Env Init...")


    # Methods needed by the RobotGazeboEnv
    # ----------------------------
    def _check_all_systems_ready(self):
        """
        Checks that all the sensors, publishers and other simulation systems are
        operational.
        """
        self._check_all_sensors_ready()
        return True

    def _check_all_sensors_ready(self):
        rospy.logdebug("START SENSOR CHECK")
        self._check_camera_image_raw_ready()
        rospy.logdebug("ALL SENSORS READY")
        
    def _check_camera_image_raw_ready(self):
        self.camera_image_raw = None
        rospy.logdebug("Waiting for /bebop/image_raw to be ready...")
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
        hls = cv2.cvtColor(img, cv2.COLOR_RGB2HLS)
        scaled = cv2.resize(hls, None, fx=0.25, fy=0.25)

        # filter by red
        lower_range = np.array([0,100,100], dtype=np.uint8)
        upper_range = np.array([125,200,200], dtype=np.uint8)
        filtered = cv2.inRange(scaled, lower_range, upper_range)

        self.camera_image_raw = filtered
    
    def _check_all_publishers_ready(self):
        """
        Checks that all the publishers are working
        """
        rospy.logdebug("START PUBLISHER CHECK")
        self._check_cmd_vel_pub_connection()
        self._check_takeoff_pub_connection()
        self._check_land_pub_connection()
        rospy.logdebug("ALL PUBLISHERS READY")

    def _check_cmd_vel_pub_connection(self):
        rate = rospy.Rate(10)
        while self._cmd_vel_pub.get_num_connections() == 0 and not rospy.is_shutdown():
            rospy.logdebug("/bebop/cmd_vel not ready yet, retrying...")
            try:
                rate.sleep()
            except rospy.ROSInterruptException:
                pass
        rospy.logdebug("/bebop/cmd_vel publisher ready =>")
        
    def _check_takeoff_pub_connection(self):
        rate = rospy.Rate(10)
        while self._takeoff_pub.get_num_connections() == 0 and not rospy.is_shutdown():
            rospy.logdebug("/bebop/takeoff not ready yet, retrying...")
            try:
                rate.sleep()
            except rospy.ROSInterruptException:
                pass
        rospy.logdebug("/bebop/takeoff publisher ready =>")
        
    def _check_land_pub_connection(self):
        rate = rospy.Rate(10)
        while self._land_pub.get_num_connections() == 0 and not rospy.is_shutdown():
            rospy.logdebug("/bebop/land not ready yet, retrying...")
            try:
                rate.sleep()
            except rospy.ROSInterruptException:
                pass
        rospy.logdebug("/bebop/land publisher ready =>")
    
    # Methods that the TrainingEnvironment will need to define here as virtual
    # because they will be used in RobotGazeboEnv GrandParentClass and defined in the
    # TrainingEnvironment.
    # ----------------------------
    def _set_init_pose(self):
        """
        Sets the Robot in its init pose
        """
        raise NotImplementedError()
    
    def _init_env_variables(self):
        """
        Inits variables needed to be initialised each time we reset at the start
        of an episode.
        """
        raise NotImplementedError()

    def _compute_reward(self, observations, done):
        """
        Calculates the reward to give based on the observations given.
        """
        raise NotImplementedError()

    def _set_action(self, action):
        """
        Applies the given action to the simulation.
        """
        raise NotImplementedError()

    def _get_obs(self):
        raise NotImplementedError()

    def _is_done(self, observations):
        """
        Checks if episode done based on observations given.
        """
        raise NotImplementedError()
        
    # Methods that the TrainingEnvironment will need.
    # ----------------------------
    
    def takeoff(self):
        """
        Sends the takeoff command and verifies it has taken off.
        Unpauses the simulation and pauses again to allow it to 
        be a self contained action.
        """

        self.gazebo.unpauseSim()
        self._check_takeoff_pub_connection()
        
        takeoff_cmd = Empty()
        self._takeoff_pub.publish(takeoff_cmd)
        
        # wait for launch to finish
        self.wait_time_for_execute_movement()
        self.gazebo.pauseSim()
        
    def land(self):
        """
        Sends the land command and verifies it has taken off.
        Unpauses the simulation and pauses again to allow it to 
        be a self contained action.
        """

        self.gazebo.unpauseSim()
        self._check_land_pub_connection()
        
        land_cmd = Empty()
        self._land_pub.publish(land_cmd)

        # wait for landing to finish
        self.wait_time_for_execute_movement()
        self.gazebo.pauseSim()
        
    def move(self, linear_speed, angular_speed):
        cmd_vel_value = Twist()
        cmd_vel_value.linear.x = 5
        cmd_vel_value.linear.y = linear_speed
        cmd_vel_value.angular.z = angular_speed

        self.speed = linear_speed
        self._check_cmd_vel_pub_connection()
        self._cmd_vel_pub.publish(cmd_vel_value)
        self.wait_time_for_execute_movement()
                                        
    def wait_time_for_execute_movement(self):
        time.sleep(1.0)
    
    def get_camera_image_raw(self):
        return self.camera_image_raw