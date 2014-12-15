import pymunk
from pymunk import Vec2d
import pyglet
from pyglet.gl import *
import math
import PiTweener

class Player(object):
	def __init__(self, scene, position=(0,0)):
		self.scene = scene

		radius, mass = 7, .001 #7.5, .001

		p_man_moment = pymunk.moment_for_circle(mass, 0, radius)

		self.p_man 						= pymunk.Body(mass, p_man_moment)
		self.p_man.position 			= position
		self.p_man_shape 				= pymunk.Circle(self.p_man, radius)
		self.p_man_shape.friction 		= .5
		self.p_man_shape.group 			= 1
		self.p_man_shape.collision_type = 1
		self.p_man_shape.elasticity 	= .2

		self.p_man_shape.fill_color = (0,0,0,0)

		scene.space.add(self.p_man, self.p_man_shape)

		pman_img = pyglet.image.load('resources/textures/pman.png')
		pman_img.anchor_x, pman_img.anchor_y = pman_img.width//2, pman_img.height//2
		tex = pman_img.get_texture()
		
		glTexParameteri(tex.target, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
		glTexParameteri(tex.target, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
		
		self.pman_s = pyglet.sprite.Sprite(
			pman_img, batch=scene.normal_batch, group=scene.ordered_group3)

		self.pman_s.scale = 1

		self.p_man.posx = 0
		self.p_man.posy = 0

		self.p_man.start_pos = position
		self.p_man.update_tween = self.update_tween
		self.p_man.on_tween_complete = self.on_tween_complete
		self.p_man.dead = False

		self.p_man.scene = scene
		
	def draw(self):
		self.pman_s.x,self.pman_s.y = self.p_man.position
		self.pman_s.rotation = math.degrees(-self.p_man.angle)

		if self.p_man.is_sleeping:
			self.p_man.activate()

	def on_tween_complete(self):
		print "done tweening"
		self.p_man.dead = False
		self.p_man.velocity = (0,0)
		self.p_man.angular_velocity = 0
		self.p_man_shape.collision_type = 1

	def update_tween(self):
		pos = (self.p_man.posx,self.p_man.posy)

		self.p_man.position = pos

class Ghost(object):
	def __init__(self, scene, tex = 'blinky', position=(0,0)):
		self.start_pos = position
		
		radius, mass = 7, .001

		p_man_moment = pymunk.moment_for_circle(mass, 0, radius)

		self.ghost_b 					= pymunk.Body(mass, p_man_moment)
		self.ghost_b.position 			= position
		self.ghost_shape 				= pymunk.Circle(self.ghost_b, radius)
		self.ghost_shape.friction 		= .5
		self.ghost_shape.elasticity 	= .2
		self.ghost_shape.collision_type = 4

		self.ghost_shape.fill_color = (0,0,0,0)

		scene.space.add(self.ghost_b, self.ghost_shape)

		ghost_img = pyglet.image.load('resources/textures/'+tex+'.png')
		ghost_img.anchor_x, ghost_img.anchor_y = ghost_img.width/2, ghost_img.height/2
		tex = ghost_img.get_texture()
		
		glTexParameteri(tex.target, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
		glTexParameteri(tex.target, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
		
		self.ghost_s = pyglet.sprite.Sprite(
			ghost_img, batch=scene.normal_batch, group=scene.ordered_group3)

		self.ghost_s.scale = 1

		self.ghost_b.on_tween_complete = self.on_tween_complete
		self.ghost_b.update_tween = self.update_tween

		self.ghost_b.posx = position[0]
		self.ghost_b.posy = position[1]
		
	def draw(self):
		self.ghost_s.x,self.ghost_s.y = self.ghost_b.position
		self.ghost_s.rotation = math.degrees(-self.ghost_b.angle)

		if self.ghost_b.is_sleeping:
			self.ghost_b.activate()

	def on_tween_complete(self):
		print "done tweening"
		self.ghost_b.velocity = (0,0)
		self.ghost_b.angular_velocity = 0

	def update_tween(self):
		pos = (self.ghost_b.posx,self.ghost_b.posy)

		self.ghost_b.position = pos

class Nums(object):
	def __init__(self, scene, point_list):

		def remove_num(space, arbiter):
			first_shape = arbiter.shapes[0] 
			space.add_post_step_callback(space.remove, first_shape)
			#first_shape.sprite.visible = False
			first_shape.glpt.vertices = [-20000,-20000]
			return False

		scene.space.add_collision_handler(2, 1, begin = remove_num)

		for point in point_list:
			num = pymunk.Circle(pymunk.Body(), 1)
			num.body.position = point
			num.collision_type = 2
			num.sensor = True
			scene.space.add(num)

			num.glpt = scene.normal_batch.add(1, pyglet.gl.GL_POINTS, scene.ordered_group2,
							('v2f', point),
							('c3B', (255,184,151)))

class Director(object):
	def __init__(self, scene):
		self.scene = scene

		self.tweener = PiTweener.Tweener()

		def kill_player(space, arbiter):
			if not arbiter.shapes[1].body.dead:

				duration = 2

				player = arbiter.shapes[1].body
				player.posx = player.position[0]
				player.posy = player.position[1]
				player.velocity = (0,0)
				player.dead = True
				arbiter.shapes[1].collision_type = 100

				## reset player position and angle
				a = math.degrees(player.angle)
				if a >= 360 or a <= -360:
					m = a % 360
					player.angle = math.radians(m)
				self.tweener.add_tween(player, tween_time=duration, tween_type=self.tweener.IN_OUT_QUAD,
					posx=player.start_pos[0], posy=player.start_pos[1], angle=0,
            	    on_complete_function=player.on_tween_complete,
            	    on_update_function=player.update_tween)
				## reset camera angle
				level = arbiter.shapes[1].body.scene.level
				a = level.board_angle
				if a >= 360 or a <= -360:
					m = a % 360
					level.board_angle = m
					arbiter.shapes[1].body.scene.camera.angle = m
				self.tweener.add_tween(level, tween_time=duration, tween_type=self.tweener.IN_OUT_QUAD,
					board_angle = 0,)
				## reset ghosts
				for ghost in [level.blinky, level.inky, level.pinky]:
					body = ghost.ghost_b
					body.posx = body.position[0]
					body.posy = body.position[1]
					a = math.degrees(body.angle)
					if a >= 360 or a <= -360:
						m = a % 360
						body.angle = math.radians(m)
					self.tweener.add_tween(body, tween_time=duration, tween_type=self.tweener.IN_OUT_QUAD,
						posx=ghost.start_pos[0], posy=ghost.start_pos[1], angle=0,
            		    on_complete_function=ghost.on_tween_complete,
            		    on_update_function=ghost.update_tween)

			return False

		self.scene.space.add_collision_handler(4, 1, begin = kill_player)

	def update(self):
		self.tweener.update()
		#time.sleep(.06)

class Power(object):
	def __init__(self, scene, point_list):
		self.power_batch = pyglet.graphics.Batch()
		def remove_pow(space, arbiter):
				first_shape = arbiter.shapes[0] 
				space.add_post_step_callback(space.remove, first_shape)
				#first_shape.sprite.visible = False
				first_shape.glpt.vertices = [-20000,-20000]
	
				return False
	
		scene.space.add_collision_handler(2, 1, begin = remove_pow)
	
		for point in point_list:
			num = pymunk.Circle(pymunk.Body(), 3)
			num.body.position = point
			num.collision_type = 2
			num.sensor = True
			scene.space.add(num)
			
			num.glpt = self.power_batch.add(1, pyglet.gl.GL_POINTS, None,
							('v2f', point),
							('c3B', (255,184,151)))
			

	def draw(self):
		glEnable( GL_POINT_SMOOTH )
		glPointSize(10)
		self.power_batch.draw()
		glPointSize(2)
		glDisable( GL_POINT_SMOOTH )