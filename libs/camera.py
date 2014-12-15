from __future__ import division
import pyglet
from pyglet.gl import *
glEnable(GL_TEXTURE_2D)
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
import math
from math import sin,cos,tan
import pymunk
from pymunk import Vec2d

import utils
import ctypes

def world_mouse(mX, mY, camera_pos_x, camera_pos_y, camera_scale, screen_resolution):
	aspect = screen_resolution[0]/screen_resolution[1]
	wmX = (camera_pos_x - (camera_scale*aspect)) + mX*((camera_scale*aspect)/screen_resolution[0])*2
	wmY = (camera_pos_x - (camera_scale)) + mY*((camera_scale)/screen_resolution[1])*2
	wmPos = wmX, wmY
	print(wmPos)
	return wmPos
	
class Camera(object):
	def __init__ (self, screen_size,
					 	pos_rate=(1,1,1), 
			         	target_rate=(1,1,1), 
			         	angle_rate=1, 
			         	fov_rate=1):
		self.screen_size 		= screen_size
		self.width, self.height = screen_size
		self.aspect 			= screen_size[0] / screen_size[1]

		self.zoom = 0
		self.pos = (0,0,0)
		self.target = (0,0,0)
		self.angle = 0
		self.fov = 90

		self.pos_rate		= pos_rate
		self.target_rate	= target_rate
		self.angle_rate		= angle_rate
		self.fov_rate		= fov_rate
		
	def update(self, pos, target, angle, fov):
		
		glViewport(0, 0, self.screen_size[0], self.screen_size[1])

		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()

		self.pos = (utils.weighted_average(self.pos[0],pos[0],self.pos_rate[0]),
					utils.weighted_average(self.pos[1],pos[1],self.pos_rate[1]),
					utils.weighted_average(self.pos[2],pos[2],self.pos_rate[2]))
		self.target = (utils.weighted_average(self.target[0],target[0],self.target_rate[0]),
					   utils.weighted_average(self.target[1],target[1],self.target_rate[1]),
					   utils.weighted_average(self.target[2],target[2],self.target_rate[2]))
		self.angle = utils.weighted_average(self.angle,angle,self.angle_rate)
		self.fov = utils.weighted_average(self.fov,fov,self.fov_rate)

		# fov (120), aspect, near, far clipping planes
		gluPerspective(self.fov, self.aspect, 10.0, -10.)

		glRotatef(self.angle,0.0,0.0,1.0)
		
		# position of the camera, target, up axis
		gluLookAt(self.pos[0], self.pos[1], self.pos[2]+self.zoom,
				  self.target[0], self.target[1], self.target[2],
				  0,1,0)

		glMatrixMode(GL_MODELVIEW)
		glLoadIdentity()

	def scroll_zoom(self, scroll_y):
		#self.scale -= scroll_y
		self.zoom -= scroll_y*5
		print self.zoom

	def ui_mode(self):
		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()
		gluOrtho2D(0, self.screen_size[0], 0, self.screen_size[1])
		glMatrixMode(GL_MODELVIEW)
		glLoadIdentity()

	def set_3d(self):
		glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
		glEnable(GL_DEPTH_TEST)         # enable depth testing
		# reset modelview matrix
		glMatrixMode(GL_MODELVIEW)
		glLoadIdentity()

	def set_2d(self):
		glDisable(GL_DEPTH_TEST)
		# store the projection matrix to restore later
		glMatrixMode(GL_PROJECTION)
		glPushMatrix()

		# load orthographic projection matrix
		glLoadIdentity()
		#glOrtho(0, float(self.width),0, float(self.height), 0, 1)
		far = 8192
		glOrtho(-self.width / 2., self.width / 2., -self.height / 2., self.height / 2., -10, far)

		# reset modelview
		glMatrixMode(GL_MODELVIEW)
		glLoadIdentity()

		#glClear(GL_COLOR_BUFFER_BIT)
	def draw_2d(self):
		glTranslatef(self.newPositionX*-1, self.newPositionY*-1, 100)

	def unset_2d(self):
		# load back the projection matrix saved before
		glMatrixMode(GL_PROJECTION)
		glPopMatrix() 