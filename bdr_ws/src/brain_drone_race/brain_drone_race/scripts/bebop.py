import rospy
from std_msgs.msg import Empty, Float32
from sensor_msgs.msg import Image
from geometry_msgs.msg import Twist
#from pynput.keyboard import Key, Listener

import cv2
from cv_bridge import CvBridge, CvBridgeError

import pyrebase
import numpy as np
#import pandas as pd
import time

class Bebop:
	def __init__(self, debug=False):
		# Variables
		self.image = None
		self.speed = 0.0
		self.max_speed = 0.1
		self.threshold = 0.15
		self.engagement = 0.0
		
		self.color = "black"
		self.ready = False
		self.done = False
		self.debug = debug
	
		self.error = 0.0
		self.last_error = 0.0
		self.yscale = -0.5
		self.zscale = -0.75
		self.kp = 0.1
		self.kd = 0.4
	
		# ROS
		self.takeoff_pub = rospy.Publisher('/bebop/takeoff', Empty, queue_size=1)
		self.land_pub    = rospy.Publisher('/bebop/land', Empty, queue_size=1)
		self.cmd_vel_pub = rospy.Publisher('/bebop/cmd_vel', Twist, queue_size=1)
		self.image_sub   = rospy.Subscriber('/bebop/image_raw', Image, self.image_callback)
		self.engagement_sub = rospy.Subscriber('/engagement', Float32, self.engagement_callback)

	
		# Firebase
		config = {
			"apiKey": "AIzaSyBTUkaNa4H9gow6V1hRvNy62r8lWaBUE9k",
    			"authDomain": "braindronerace.firebaseapp.com",
			"databaseURL": "https://braindronerace.firebaseio.com",
			"projectId": "braindronerace",
			"storageBucket": "braindronerace.appspot.com",
			"messagingSenderId": "743801530945"
		}
		self.firebase = pyrebase.initialize_app(config)
		self.db = self.firebase.database()
	
		# Keyboard Listener
		#self.listener = Listener(on_press=self.on_press)
		#self.listener.start()
	
		# Setup Routine
		rospy.init_node('brain_drone_race', anonymous=True, log_level=rospy.WARN)
		self.check_all_sensors_ready()
		rospy.logwarn("Race environment successfully initialized")
		
	#def on_press(self, key):
	#	try:
	#		if key == Key.space:
	#			self.done = True
	#	except AttributeError:
	#		pass	
	
	def takeoff(self):
		self.wait_for_start()
		self.wait(5.0)
		self.wait_for_engagement()
		
		takeoff_cmd = Empty()
		self.check_publisher_ready(self.takeoff_pub, "/bebop/takeoff")
		self.takeoff_pub.publish(takeoff_cmd)
		
		self.done = False
		self.wait(5.0)
		
	def land(self):
		land_cmd = Empty()        
		self.check_publisher_ready(self.land_pub, "/bebop/land") 
		self.land_pub.publish(land_cmd)

	def wait_for_engagement(self):
		engagement = self.engagement
		while engagement < self.threshold:
			engagement = self.engagement
		print("engagement threshold met")

	def wait_for_start(self):
		status = self.db.child('status/status/value').get().val()
		print("initial status", status)
		while status != "START":
			status = self.db.child('status/status/value').get().val()
		print("status is ready")
			
	def land_on_stop(self):
		status = self.db.child('status/status/value').get().val()
		if status == "STOP":
			self.land()
			self.done = True

	def set_error(self):
		h, w = self.image.shape[:2]
		wall = w//5

		r1 = np.sum(self.image[0:h, 0*wall:1*wall] == 255)
		r2 = np.sum(self.image[0:h, 1*wall:2*wall] == 255)
		r3 = np.sum(self.image[0:h, 2*wall:3*wall] == 255)
		r4 = np.sum(self.image[0:h, 3*wall:4*wall] == 255)
		r5 = np.sum(self.image[0:h, 4*wall:5*wall] == 255)
		
		region = max(r1, r2, r3, r4, r5)
		self.last_error = self.error

		if region == r1:
			self.error = -2
		elif region == r2:
			self.error = -1
		elif region == r3:
			self.error = 0
		elif region == r4:
			self.error = 1
		else:
			self.error = 2

	def move(self):
		self.land_on_stop() 
		self.set_error()
		y = self.yscale * (self.kp * self.error + self.kd * (self.error - self.last_error))
		z = self.zscale * (self.kp * self.error + self.kd * (self.error - self.last_error))
		
		speed = self.scale(self.max_speed, self.engagement)
		
		if self.debug:
			print("engagement:", self.engagement)
			print("speed:", speed)
			print("action:", y, z)

		velocity_cmd = Twist()
		velocity_cmd.linear.x  = speed
		velocity_cmd.linear.y  = y
		velocity_cmd.angular.z = z

		self.check_publisher_ready(self.cmd_vel_pub, "/bebop/cmd_vel")
		self.cmd_vel_pub.publish(velocity_cmd)
		self.wait()
										
	def wait(self, ms = 0.1):
		time.sleep(ms)

	def scale(self, factor, delta):
		return factor * np.clip(delta, 0, 1)
		
	def check_all_sensors_ready(self):
		self.check_publisher_ready(self.takeoff_pub, "/bebop/takeoff")
		self.check_publisher_ready(self.land_pub,    "/bebop/land")
		self.check_publisher_ready(self.cmd_vel_pub, "/bebop/cmd_vel")
		self.check_camera_image_ready()
		
	def check_publisher_ready(self, publisher, name):
		rate = rospy.Rate(10)
		while publisher.get_num_connections() == 0 and not rospy.is_shutdown():
			rospy.logerr(name + " not ready yet, retrying...")
			try:
				rate.sleep()
			except rospy.ROSInterruptException:
				pass
		rospy.logwarn(name + " ready")
		
	def check_camera_image_ready(self):
		rospy.logerr("Waiting for /bebop/image_raw to be ready...")
		while self.image is None and not rospy.is_shutdown():
			try:
				self.image = rospy.wait_for_message("/bebop/image_raw", Image, timeout=5.0)
				rospy.logdebug("/bebop/image_raw ready")
			except:
				rospy.logerr("/bebop/image_raw not ready yet, retrying...")
		return self.image
		
	def image_callback(self, data):
		bridge = CvBridge()
		img = bridge.imgmsg_to_cv2(data, "bgr8")

		# color filtering
		if self.color == "black":
			gray  = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
			lower = np.array([0],  dtype=np.uint8)
			upper = np.array([55], dtype=np.uint8)
			filtered = cv2.inRange(gray, lower, upper)

		elif self.color == "white":
			lower = np.array([200, 200, 200],   dtype=np.uint8)
			upper = np.array([255, 255, 255], dtype=np.uint8)
			filtered = cv2.inRange(img, lower, upper)
		
		if self.debug:
			cv2.namedWindow('masked image', cv2.WINDOW_NORMAL)
			cv2.imshow('masked image', filtered)
			cv2.waitKey(1)

		self.image = filtered
		
	def engagement_callback(self, data):
		self.engagement = data.data
	
