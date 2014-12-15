from __future__ import division
import os, sys
import pyglet
from pyglet.gl import *
import pymunk
from pymunk import Vec2d
import math
from math import sin,cos,tan,degrees,sqrt,atan2,radians
import random
import utils

pyglet.resource.path = ['resources']
pyglet.resource.reindex()

def define_circle_points(radius, position, res):
	# res must be divisible by three!
	res = 360//res
	add 	= (res*3.14)/180
	angle 	= 0
	points 	= []
	#res = 360//res
	iter_count = 360//res
	for i in xrange(iter_count):
		x = radius*cos(angle) + position[0]
		y = radius*sin(angle) + position[1]
		points.append(x)
		points.append(y)
		angle += add
	return points

def calc_index(length):
	index = []
	index.append(0)
	for i in xrange(length):
		if i != 0:
			index.append(i)
			index.append(i)
	index.append(0)
	#print(index)
	return index

def calc_line_index(length):
	index = []
	index.append(0)
	for i in xrange(length):
		if i != 0:
			index.append(i)
			if (i+1) != length:
				index.append(i)
	#print(index)
	return index

def calc_index_tri(length):
	index = []
	for i in xrange(length):
		if ((i+1) % 3) != 0:
			index.append(i)
		else:
			index.append(i)
			if length > 3:
				index.append(i)
		if (i+1) == length and length > 3:
			index.append(0)
	#print(index)
	return index

def calc_circle_index(length):
	index = []
	for i in xrange(length):
		if i < length-2:
			index.append(0)
			index.append(i+1)
			index.append(i+2)
		else:
			index.append(0)
			index.append(1)
			index.append(length-1)
	return index

class PymunkUtil2(object):
	def __init__(self, scene):
		self.scene = scene
		self.space = scene.space
		self.segments 	= []
		self.polygons  	= []
		self.circles  	= []

		for shape in self.space.shapes:
			if isinstance(shape, pymunk.Segment):
				self.segments.append(shape)
			if isinstance(shape, pymunk.Circle):
				self.circles.append(shape)
			if isinstance(shape, pymunk.Poly):
				self.polygons.append(shape)

		print('Number of shapes: '+str(len(self.scene.space.shapes)))
		print('Number of bodies: '+str(len(self.scene.space.bodies)))

		self.circle_sleep_fill 	= (200,200,200,255)
		self.poly_sleep_fill 	= (200,200,200,120)

		self.sleep_color 		= (200,200,200)

		opacity = 255
		self.rand_colors 		= [(225,20,25,opacity),(20,227,25,opacity),(25,20,225,opacity),
								   (225,250,30,opacity),(24,210,225,opacity),(225,20,210,opacity),
								   (245,100,17,opacity)]

		self.seg_color = (100,110,190)

	def setup(self):
		for segment in self.segments:
			length = utils.distance(segment.a, segment.b)
			angle = utils.angle_between_points(segment.a, segment.b)

			verts = [Vec2d(-length/2, segment.radius), Vec2d(length/2, segment.radius),
					 Vec2d(length/2, -segment.radius), Vec2d(-length/2, -segment.radius)]

			cap_l = [Vec2d(-length/2, segment.radius), 
					 Vec2d(-length/2, -segment.radius), 
					 Vec2d((-length/2)-segment.radius, 0),]
			cap_r = [Vec2d(length/2, segment.radius), 
					 Vec2d(length/2, -segment.radius), 
					 Vec2d((length/2)+segment.radius, 0),]

			for vert in verts:
				vert.rotate_degrees(angle)
				vert += utils.midpoint(segment.a, segment.b)

			points = []
			for vert in verts:
				points.append(vert[0])
				points.append(vert[1])

			res = len(points)//2
			
			segment.pyglet_debug = self.scene.debug_batch.add_indexed(res, GL_TRIANGLES, self.scene.ordered_group1,
																	  calc_index_tri(res),
									  								  ('v2f', points),
									  								  ('c3B', self.seg_color*res))

			# Segment end caps
			for vert in cap_l:
				vert.rotate_degrees(angle)
				vert += utils.midpoint(segment.a, segment.b)

			points = []
			for vert in cap_l:
				points.append(vert[0])
				points.append(vert[1])

			segment.cap_l = self.scene.debug_batch.add_indexed(3, GL_TRIANGLES, self.scene.ordered_group1,
													   calc_index_tri(3),
									  				   ('v2f', points),
									  				   ('c3B', self.seg_color*3))

			for vert in cap_r:
				vert.rotate_degrees(angle)
				vert += utils.midpoint(segment.a, segment.b)

			points = []
			for vert in cap_r:
				points.append(vert[0])
				points.append(vert[1])

			segment.cap_r = self.scene.debug_batch.add_indexed(3, GL_TRIANGLES, self.scene.ordered_group1,
													   calc_index_tri(3),
									  				   ('v2f', points),
									  				   ('c3B', self.seg_color*3))
			

		for circle in self.circles:
			if not hasattr(circle,'fill_color'):
				circle.fill_color 	= random.choice(self.rand_colors)
			circle.outline_color 	= (255,255,255)
			circle.line_color 		= (255,255,255)
			circle.sleep_color 		= self.sleep_color

			# divisible by 3!
			if circle.radius <= 150:
				circle.circle_res = 21
			if circle.radius <= 100:
				circle.circle_res = 18
			if circle.radius <= 50:
				circle.circle_res = 15
			if circle.radius <= 25:
				circle.circle_res = 12
			if circle.radius <= 10:
				circle.circle_res = 9
			if circle.radius <= 5:
				circle.circle_res = 6
			if circle.radius <= 2:
				circle.circle_res = 3
			

			points = define_circle_points(circle.radius, circle.body.position, circle.circle_res)

			res = len(points)//2
			circle.res = res

			circle.pyglet_outline = self.scene.debug_batch.add_indexed(res, GL_LINES, self.scene.ordered_group3,
													  					calc_index(res),
													  					('v2f', points),
											  		  					('c3B', (255,255,255)*res))

			fill_points = points
			fill_points.insert(0, circle.body.position[0])
			fill_points.insert(1, circle.body.position[1])
			
			circle.pyglet_fill = self.scene.debug_batch.add_indexed(res+1, GL_TRIANGLES, self.scene.ordered_group4,
													  					  calc_circle_index(res+1),
													  					  ('v2f', fill_points),
											  		  					  ('c4B', circle.fill_color*(res+1)))
			

			circle.rotation_line = self.scene.debug_batch.add_indexed(2, GL_LINES, self.scene.ordered_group5,
													  				  [0,1,1,0],
													  				  ('v2f', (0,0,0,0)),
											  		  				  ('c3B', (255,255,255)*2))
		for poly in self.polygons:
			if not hasattr(poly,'fill_color'):
				poly.fill_color 	= random.choice(self.rand_colors)
				poly.outline_color 	= (255,255,255,255)
			poly.sleep_fill_color 	= self.poly_sleep_fill
			poly.sleep_color 		= (255,255,255,255)
			poly.outline_color 		= (255,255,255,255)

			p = poly.get_points()#.get_vertices()
			points = []
			for vert in p:
				points.append(vert[0])
				points.append(vert[1])

			res = len(points)//2
			poly.res = res

			# fill and outline for polygons
			poly.pyglet_fill = self.scene.debug_batch.add_indexed(res, GL_TRIANGLES, self.scene.ordered_group2,
													  			  calc_index_tri(res),
													  			  ('v2f', points),
											  		  			  ('c4B', (0,0,0,0)*res))

			poly.pyglet_outline = self.scene.debug_batch.add_indexed(res, GL_LINES, self.scene.ordered_group1,
													  			   	 calc_index(res),
													  			   	 ('v2f', points),
											  		  			   	 ('c4B', poly.outline_color*res))

	def update(self):
		self.update_circles()
		self.update_polys()

	def update_circles(self):
		# update active circles
		for circle in self.circles:
			if not circle.body.is_rogue and not circle.body.is_sleeping:
				circle.pyglet_outline.vertices = define_circle_points(circle.radius, circle.body.position, circle.circle_res)
				x = circle.radius*cos(circle.body.angle) + circle.body.position[0]
				y = circle.radius*sin(circle.body.angle) + circle.body.position[1]
				circle.rotation_line.vertices = (circle.body.position[0], circle.body.position[1], x, y)

				fill_points = list(circle.pyglet_outline.vertices)
				fill_points.insert(0, circle.body.position[0])
				fill_points.insert(1, circle.body.position[1])
				circle.pyglet_fill.vertices = fill_points

				# sleepy colors
				circle.pyglet_outline.colors 	= circle.outline_color*circle.res
				circle.pyglet_fill.colors 		= circle.fill_color*(circle.res+1)
			else:
				circle.pyglet_outline.colors 	= circle.sleep_color*circle.res
				circle.pyglet_fill.colors 		= self.circle_sleep_fill*(circle.res+1)

	def update_polys(self):
		# update active polygons
		for poly in self.polygons:
			if not poly.body.is_rogue and not poly.body.is_sleeping:
				p = poly.get_points()#.get_vertices()
				points = []
				for vert in p:
					points.append(vert[0])
					points.append(vert[1])
				poly.pyglet_outline.vertices, poly.pyglet_fill.vertices = points,points	# outline points set here 
																							# (may be intensive, i don't know)

				# sleepy colors
				poly.pyglet_fill.colors 	= poly.fill_color*poly.res
				poly.pyglet_outline.colors 	= poly.outline_color*poly.res 					# outline
			else:
				poly.pyglet_fill.colors 	= poly.sleep_fill_color*poly.res
				poly.pyglet_outline.colors 	= poly.sleep_color*poly.res 					# outline

class MouseInteraction(object):
	def __init__(self, scene):
		self.scene = scene
		self.space = scene.space

		self.aspect = self.scene.screen_resolution[0]/self.scene.screen_resolution[1]

		for shape in self.space.shapes:
			shape.grabbable = False

		self.cursor_body = pymunk.Body(pymunk.inf, pymunk.inf)
		self.cursor_constraint = None
		self.grabbable_shape = None

	def world_mouse(self, x, y):
		
		wX = (self.scene.camera.newPositionX - (self.scene.camera.newWeightedScale*self.aspect)) \
							+ x*((self.scene.camera.newWeightedScale*self.aspect)/self.scene.screen_resolution[0])*2 
		wY = (self.scene.camera.newPositionY - (self.scene.camera.newWeightedScale)) \
							+ y*((self.scene.camera.newWeightedScale)/self.scene.screen_resolution[1])*2
		
		wPos = wX, wY
		return wPos

	def on_mouse_motion(self, mp):
		pass
		#mp = self.world_mouse(mp[0], mp[1])

	def on_mouse_press(self, mp, mb):
		mp = self.world_mouse(mp[0], mp[1])

		# query the shapes
		self.grabbable_shape = self.space.point_query_first(mp)
		# check if the shape is static
		# if it is, don't make a constraint for it
		if self.grabbable_shape != None:
			if self.grabbable_shape.body.is_static:
				self.grabbable_shape = None

		print(mp)
		self.cursor_body.position = mp
		if self.grabbable_shape != None and mb == pyglet.window.mouse.LEFT:
			
			offset = Vec2d(mp) - self.grabbable_shape.body.position
			offset = offset.rotated(-self.grabbable_shape.body.angle)

			print(self.grabbable_shape.body.mass)

			stiff = self.grabbable_shape.body.mass*100
			damp = self.grabbable_shape.body.mass*5

			self.cursor_constraint = pymunk.constraint.DampedSpring(self.cursor_body, self.grabbable_shape.body, 
																    (0,0), (offset), 2, stiff, damp)
			
			#self.cursor_constraint = pymunk.constraint.PivotJoint(self.cursor_body, self.grabbable_shape.body, Vec2d(0,0), offset)

			self.space.add(self.cursor_constraint)

	def on_mouse_drag(self, mp, mb):
		mp = self.world_mouse(mp[0], mp[1])
		current = self.cursor_body.position
		if self.grabbable_shape != None and mb == pyglet.window.mouse.LEFT:
			self.cursor_body.position = mp
			#self.cursor_body.velocity = (mp - current) / (1.0/60.0)
			pass

	def on_mouse_release(self, mp, mb):
		if self.grabbable_shape != None and mb == pyglet.window.mouse.LEFT:
			self.space.remove(self.cursor_constraint)

def getSmoothConfig():
	# http://www.akeric.com/blog/?p=1510
	"""
	Sets up a configuration that allows of smoothing/antialiasing.
	The return of this is passed to the config parameter of the created window.
	"""
	try:
	    # Try and create a window config with multisampling (antialiasing)
	    config = Config(sample_buffers = 1, samples = 4,
	                    depth_size = 16, double_buffer=True)
	except pyglet.window.NoSuchConfigException:
	    print ("Smooth contex could not be aquiried.")
	    config = None
	return config