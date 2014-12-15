import pymunk
from pymunk import Vec2d
import pyglet
from pyglet.gl import *
import math

class Car(object):
	def __init__(self, space, position=(0,0)):
		mass = .05

		moment = pymunk.moment_for_box(mass, 80, 40)

		self.body = pymunk.Body(mass, moment)
		self.body.position = position

		self.body.angular_velocity_limit = 11

		bot_left, bot_right = (-40,-13),(40,-13)

		shapes = [pymunk.Poly(self.body, [(-40,2 ),bot_left,bot_right]),
				  pymunk.Poly(self.body, [bot_right,(-40,2  ),(40,5  )]),
				  pymunk.Poly(self.body, [(40,5  ),(-40,2  ),(-25,20)]),
				  pymunk.Poly(self.body, [(-25,20),( 40,5  ),(2,20  )])]

		for shape in shapes:
			shape.friction 		= .2
			shape.group 		= 1
			shape.elasticity 	= .6

			shape.fill_color 	=  (250,20,70,255)

		space.add(self.body)
		space.add(shapes)


		wheel_color = (90,140,190,255)


		radius 				= 13
		wheel_mass 			= .01
		wheel_friction 		= 1.2
		wheel_elasticity 	= .0

		wheel_moment = pymunk.moment_for_circle(wheel_mass, 0, radius)
		
		l_wheel_base = 24 # 24
		self.l_wheel_body 			= pymunk.Body(wheel_mass, wheel_moment)
		self.l_wheel_body.position 	= (self.body.position[0]-l_wheel_base, self.body.position[1]-20)
		l_wheel_shape 				= pymunk.Circle(self.l_wheel_body, radius)
		l_wheel_shape.friction 		= wheel_friction
		l_wheel_shape.group 		= 1
		l_wheel_shape.elasticity 	= wheel_elasticity

		l_wheel_shape.fill_color 	= wheel_color

		r_wheel_base = 24
		self.r_wheel_body 			= pymunk.Body(wheel_mass, wheel_moment)
		self.r_wheel_body.position 	= (self.body.position[0]+r_wheel_base, self.body.position[1]-20)
		r_wheel_shape 				= pymunk.Circle(self.r_wheel_body, radius)
		r_wheel_shape.friction 		= wheel_friction
		r_wheel_shape.group 		= 1
		r_wheel_shape.elasticity 	= wheel_elasticity

		r_wheel_shape.fill_color 	= wheel_color

		space.add(self.l_wheel_body, self.r_wheel_body, 
				  l_wheel_shape, r_wheel_shape)

		rest_ln     = 43  	# 43
		stiff       = 7   	# 10
		damp        = .13  	# .2

		up_limit 	= -5 # -10
		down_limit 	= -25 # -28

		left_spring  = pymunk.constraint.DampedSpring(self.body, 
													  self.l_wheel_body, 
													  (-l_wheel_base, 20),  
													  (0,0), 
													  rest_ln, 
													  stiff, 
													  damp)
		right_spring = pymunk.constraint.DampedSpring(self.body, 
													  self.r_wheel_body, 
													  (r_wheel_base, 20),   
													  (0,0), 
													  rest_ln, 
													  stiff, 
													  damp)

		left_groove  = pymunk.constraint.GrooveJoint(self.body, 
													 self.l_wheel_body, 
													 (-l_wheel_base, up_limit), 
													 (-l_wheel_base, down_limit),  
													 (0,0))
		right_groove = pymunk.constraint.GrooveJoint(self.body, 
													 self.r_wheel_body, 
													 (r_wheel_base, up_limit),  
													 (r_wheel_base, down_limit), 
													 (0,0))

		space.add(left_spring,left_groove,right_spring,right_groove)

		## antenna

		tmp = []
		size = 3,10
		box_moment = pymunk.moment_for_box(.01, size[0], size[1])
		offset = 0
		for i in range(3):
			box_body = pymunk.Body(.0001, box_moment)
			box_body.position = self.body.position + Vec2d(-24,20+(size[1]//2)+offset)
			box_shape = pymunk.Poly.create_box(box_body, size=size)
			box_shape.group = 1
			box_shape.friction = .3
			box_shape.elasticity = .5

			box_shape.fill_color = (120,120,120,255)

			tmp.append(box_body)

			if i == 0:
				pin_const = pymunk.constraint.PivotJoint(self.body, box_body, Vec2d(-24,20), Vec2d(0,(-size[1]/2)+1))
				spr_const = pymunk.constraint.DampedRotarySpring(self.body, box_body, 0, 100, .8)
			else:
				pin_const = pymunk.constraint.PivotJoint(tmp[i-1], box_body, Vec2d(0,(size[1]/2)-1), Vec2d(0,(-size[1]/2)+1))
				spr_const = pymunk.constraint.DampedRotarySpring(tmp[i-1], box_body, 0, 100, .8)

			offset += size[1]-1

			space.add(box_body, box_shape, pin_const, spr_const)

	def control(self, keys):
		if pyglet.window.key.LEFT in keys:
			self.body.angular_velocity += .7
		if pyglet.window.key.RIGHT in keys:
			self.body.angular_velocity -= .7

		if abs(self.l_wheel_body.angular_velocity) < 120:
			if pyglet.window.key.UP in keys:
				self.l_wheel_body.angular_velocity -= 11
			elif pyglet.window.key.DOWN in keys:
				self.l_wheel_body.angular_velocity += 11
				
		if not pyglet.window.key.UP  	in keys or \
		   not pyglet.window.key.DOWN 	in keys:
			self.l_wheel_body.angular_velocity *= .95 # fake friction for wheels
			self.r_wheel_body.angular_velocity *= .99

		if pyglet.window.key.SPACE in keys:
			self.body.apply_impulse((0,7))

		if self.body.is_sleeping:
			self.body.activate()
		if self.l_wheel_body.is_sleeping:
			self.l_wheel_body.activate()
		if self.r_wheel_body.is_sleeping:
			self.r_wheel_body.activate()
	def draw(self):
		pass

class Jeep(object):
	def __init__(self, scene, position=(0,0)):

		mass = .002 #.02
		moment = pymunk.moment_for_box(mass, 80, 40)

		self.body 						 = pymunk.Body(mass, moment)
		self.body.position 				 = position
		self.body.angular_velocity_limit = 11
		bot_left, bot_right 			 = (-30,-14.5),(30,-14.5)

		shapes = [pymunk.Poly(self.body, [(9,2), bot_left, bot_right]),
				  pymunk.Poly(self.body, [bot_right, (9,2), (28,1)]),
				  pymunk.Poly(self.body, [(9,2), (5,14), bot_left]),
				  pymunk.Poly(self.body, [(5,14), (-26,14), bot_left])]

		for shape in shapes:
			shape.friction 		= .2
			shape.group 		= 1
			shape.elasticity 	= .6
			shape.fill_color 	=  (250,20,70,0)
			shape.outline_color =  (255,255,255,0)

		scene.space.add(self.body)
		scene.space.add(shapes)

		wheel_color = (90,140,190,255)

		radius 				= 8
		wheel_mass 			= .001 #.01
		wheel_friction 		= 1.2
		wheel_elasticity 	= .0

		wheel_moment = pymunk.moment_for_circle(wheel_mass, 0, radius)
		
		l_wheel_base = 18 # 24
		self.l_wheel_body 			= pymunk.Body(wheel_mass, wheel_moment)
		self.l_wheel_body.position 	= (self.body.position[0]-l_wheel_base, self.body.position[1]-20)
		l_wheel_shape 				= pymunk.Circle(self.l_wheel_body, radius)
		l_wheel_shape.friction 		= wheel_friction
		l_wheel_shape.group 		= 1
		l_wheel_shape.elasticity 	= wheel_elasticity

		l_wheel_shape.fill_color 	= wheel_color

		r_wheel_base = 18
		self.r_wheel_body 			= pymunk.Body(wheel_mass, wheel_moment)
		self.r_wheel_body.position 	= (self.body.position[0]+r_wheel_base, self.body.position[1]-20)
		r_wheel_shape 				= pymunk.Circle(self.r_wheel_body, radius)
		r_wheel_shape.friction 		= wheel_friction
		r_wheel_shape.group 		= 1
		r_wheel_shape.elasticity 	= wheel_elasticity

		r_wheel_shape.fill_color 	= wheel_color

		scene.space.add(self.l_wheel_body, self.r_wheel_body, 
				  l_wheel_shape, r_wheel_shape)

		rest_ln     = 40  	# 40
		stiff       = .9   	# 7
		damp        = .013  # .13
		up_limit 	= -16 	# -16
		down_limit 	= -20 	# -20

		left_spring  = pymunk.constraint.DampedSpring(self.body, 
													  self.l_wheel_body, 
													  (-l_wheel_base, 20),  
													  (0,0), 
													  rest_ln, 
													  stiff, 
													  damp)
		right_spring = pymunk.constraint.DampedSpring(self.body, 
													  self.r_wheel_body, 
													  (r_wheel_base, 20),   
													  (0,0), 
													  rest_ln, 
													  stiff, 
													  damp)
		left_groove  = pymunk.constraint.GrooveJoint(self.body, 
													 self.l_wheel_body, 
													 (-l_wheel_base, up_limit), 
													 (-l_wheel_base, down_limit),  
													 (0,0))
		right_groove = pymunk.constraint.GrooveJoint(self.body, 
													 self.r_wheel_body, 
													 (r_wheel_base, up_limit),  
													 (r_wheel_base, down_limit), 
													 (0,0))

		scene.space.add(left_spring, left_groove, right_spring, right_groove)

		jeep_img = pyglet.image.load('resources/jeep.png')
		jeep_img.anchor_x, jeep_img.anchor_y = jeep_img.width//2, jeep_img.height//2
		tex = jeep_img.get_texture()
		glTexParameteri(tex.target, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
		glTexParameteri(tex.target, GL_TEXTURE_MAG_FILTER, GL_NEAREST)

		wheel_img = pyglet.image.load('resources/wheel.png')
		wheel_img.anchor_x, wheel_img.anchor_y = wheel_img.width//2, wheel_img.height//2
		tex = wheel_img.get_texture()
		glTexParameteri(tex.target, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
		glTexParameteri(tex.target, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
		
		self.chassis_s = pyglet.sprite.Sprite(
			jeep_img, batch=scene.normal_batch, group=scene.ordered_group2)
		self.l_wheel_s = pyglet.sprite.Sprite(
			wheel_img, batch=scene.normal_batch, group=scene.ordered_group3)
		self.r_wheel_s = pyglet.sprite.Sprite(
			wheel_img, batch=scene.normal_batch, group=scene.ordered_group3)
		
	def control(self, keys):
		if pyglet.window.key.LEFT in keys:
			self.body.angular_velocity += .9
		if pyglet.window.key.RIGHT in keys:
			self.body.angular_velocity -= .9

		if abs(self.l_wheel_body.angular_velocity) < 120:
			if pyglet.window.key.UP in keys:
				self.l_wheel_body.angular_velocity -= 11
			elif pyglet.window.key.DOWN in keys:
				self.l_wheel_body.angular_velocity += 11
				
		if not pyglet.window.key.UP  	in keys or \
		   not pyglet.window.key.DOWN 	in keys:
			self.l_wheel_body.angular_velocity *= .95 # fake friction for wheels
			self.r_wheel_body.angular_velocity *= .99

		if pyglet.window.key.SPACE in keys:
			self.body.apply_impulse((0,7))

		if self.body.is_sleeping:
			self.body.activate()
		if self.l_wheel_body.is_sleeping:
			self.l_wheel_body.activate()
		if self.r_wheel_body.is_sleeping:
			self.r_wheel_body.activate()

	def draw(self):
		self.chassis_s.set_position(self.body.position[0],#+(self.body.velocity[0]*.015), 
			self.body.position[1]#+(self.body.velocity[1]*.015)
				)
		self.chassis_s.rotation = math.degrees(-self.body.angle)

		self.l_wheel_s.set_position(self.l_wheel_body.position[0],#+(self.l_wheel_body.velocity[0]*.015), 
			self.l_wheel_body.position[1]#+(self.l_wheel_body.velocity[1]*.015)
				)
		self.l_wheel_s.rotation = math.degrees(-self.l_wheel_body.angle)

		self.r_wheel_s.set_position(self.r_wheel_body.position[0],#+(self.r_wheel_body.velocity[0]*.015), 
			self.r_wheel_body.position[1]#+(self.r_wheel_body.velocity[1]*.015)
				)
		self.r_wheel_s.rotation = math.degrees(-self.r_wheel_body.angle)