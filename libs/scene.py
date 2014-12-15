import os, sys
import pyglet
from pyglet.gl import *
'''
import pymunkoptions
pymunkoptions.options["debug"] = False
'''
import pymunk
from pymunk import Vec2d
import math
from math import sin,cos,tan,degrees,sqrt,atan2,radians

import pyglet_util
import camera
import vehicle
from heightmap import Contour

import entities
import utils
import meshpy

import obj_batch
import ctypes
import entities

def angle_between_lines(line1, line2):
	dx1 = line1[1][0] - line1[0][0]
	dy1 = line1[1][1] - line1[0][1]

	dx2 = line2[1][0] - line2[0][0]
	dy2 = line2[1][1] - line2[0][1]

	d = dx1*dx2 + dy1*dy2
	l2 = (dx1*dx1+dy1*dy1)*(dx2*dx2+dy2*dy2)

	return math.acos(d/math.sqrt(l2))

def clear_space(space):
	for c in space.constraints:
		space.remove(c)
	for s in space.shapes:
		space.remove(s)
	for b in space.bodies:
		space.remove(b)
		

def round_trip_connect(start, end):
	result = []
	for i in range(start, end):
	  result.append((i, i+1))
	result.append((end, start))
	return result

class GameLevel1(object):
	def __init__(self):
		pass
	def define_level(self, scene):
		self.scene = scene

		lvlc = Contour('resources/levels/level1/lvl.bmp')
		lvlc.create_segments(scene.space, radius=1, friction=.8, elasticity=1)

		self.player = entities.Player(scene, (0,-64.5))

		lvlnums = Contour('resources/levels/level1/num.bmp')

		numpts = lvlnums.points()
		print len(numpts)

		entities.Nums(scene, numpts[1::2])
		self.power = entities.Power(scene, [(0,0),])

		self.board_angle = 0

		board_img = pyglet.image.load('resources/textures/board.png')
		board_img.anchor_x, board_img.anchor_y = board_img.width//2, board_img.height//2
		tex = board_img.get_texture()

		glTexParameteri(tex.target, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
		glTexParameteri(tex.target, GL_TEXTURE_MAG_FILTER, GL_NEAREST)

		self.board_s = pyglet.sprite.Sprite(
			board_img, batch=scene.normal_batch, group=scene.ordered_group2)
		self.board_s.scale = 1


		self.blinky = entities.Ghost(scene, 'blinky', (0,33.5))
		self.inky 	= entities.Ghost(scene, 'inky', (-20,33.5))
		self.pinky 	= entities.Ghost(scene, 'pinky', (20,33.5))

		self.director = entities.Director(scene)

	def update_controls(self, keys):
		if pyglet.window.key.LEFT in keys:
			self.board_angle += 6
		if pyglet.window.key.RIGHT in keys:
			self.board_angle -= 6

	def draw(self):
		self.director.update()

		self.player.draw()

		self.blinky.draw()
		self.inky.draw()
		self.pinky.draw()

		self.power.draw()

	def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
		self.board_angle += dx/2
		
class Scene(object):
	def __init__(self, window, level):
		pass
	def update(self, dt):
		raise NotImplementedError
	def update_half(self, dt):
		raise NotImplementedError
	def update_third(self, dt):
		raise NotImplementedError
	def world_pos(self, x, y):
		raise NotImplementedError
	def keyboard_input(self, dt):
		raise NotImplementedError
	def on_key_press(self, symbol, modifiers):
		raise NotImplementedError
	def on_key_release(self, symbol, modifiers):
		raise NotImplementedError
	def on_mouse_press(self, x, y, button, modifierse):
		raise NotImplementedError
	def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
		raise NotImplementedError
	def on_mouse_release(self, x, y, button, modifiers):
		raise NotImplementedError
	def on_mouse_motion(self, x, y, dx, dy):
		raise NotImplementedError
	def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
		raise NotImplementedError

class Pymunk_Scene(Scene):
	def __init__(self, window, level):
		super(Pymunk_Scene, self).__init__(window, level)
		self.screen_resolution 	= window.width,window.height
		self.window 			= window

		self.debug_batch 		= pyglet.graphics.Batch()
		self.normal_batch 		= pyglet.graphics.Batch()
		self.ui_batch 			= pyglet.graphics.Batch()

		# The common_group parent keeps groups from 
		# overlapping on accident. Silly Pyglet!
		common_group 			= pyglet.graphics.OrderedGroup(1) 
		self.ordered_group10	= pyglet.graphics.OrderedGroup(10, 	parent = common_group)
		self.ordered_group9 	= pyglet.graphics.OrderedGroup(9, 	parent = common_group)
		self.ordered_group8 	= pyglet.graphics.OrderedGroup(8, 	parent = common_group)
		self.ordered_group7		= pyglet.graphics.OrderedGroup(7, 	parent = common_group)
		self.ordered_group6		= pyglet.graphics.OrderedGroup(6, 	parent = common_group)
		self.ordered_group5		= pyglet.graphics.OrderedGroup(5, 	parent = common_group)
		self.ordered_group4		= pyglet.graphics.OrderedGroup(4, 	parent = common_group)
		self.ordered_group3 	= pyglet.graphics.OrderedGroup(3,	parent = common_group)
		self.ordered_group2		= pyglet.graphics.OrderedGroup(2, 	parent = common_group)
		self.ordered_group1		= pyglet.graphics.OrderedGroup(1, 	parent = common_group)

		self.grav 				= (0,-600)

		self.space 						= pymunk.Space()
		self.space.sleep_time_threshold = 1
		self.space.gravity 				= self.grav

		glEnable(GL_BLEND)
		glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

		glHint(GL_POINT_SMOOTH_HINT, GL_FASTEST)

		glPointSize(2)
		glLineWidth(1) #(1.25)

		self.camera = camera.Camera(self.screen_resolution,
									pos_rate=(1,1,1), 
									target_rate=(1,1,1), 
									angle_rate=10, 
									fov_rate=1)

		#### Level ####
		self.level = level
		self.level.define_level(self)
		#### Level ####

		self.pymunk_util = pyglet_util.PymunkUtil2(self)
		self.pymunk_util.setup()

		self.keys_held = []

		self.debug = False

	def update(self, dt):
		self.space.step(dt)

		self.space.gravity = pymunk.vec2d.Vec2d(self.grav).rotated(-math.radians(self.level.board_angle))

	def update_half(self, dt):
		self.level.update_controls(self.keys_held)
		
	def update_third(self, dt):
		pass

	def draw(self):
		
		#self.pymunk_util.update()
		self.camera.update((self.level.player.p_man.position[0],self.level.player.p_man.position[1],261), 
						   (self.level.player.p_man.position[0],self.level.player.p_man.position[1],0), 
						   self.level.board_angle, 90)

		glClearColor(0,0,0,1)

		self.camera.set_3d()

		self.level.draw()
		if self.debug:
			self.pymunk_util.update()
			self.debug_batch.draw()
		self.normal_batch.draw()
		self.level.draw()

		self.camera.ui_mode()
		self.ui_batch.draw()

	def world_pos(self, x, y):
		# Depends on the position of the camera.
		pass
	def keyboard_input(self, dt):
		pass
	def on_key_press(self, symbol, modifiers):
		pass
	def on_key_release(self, symbol, modifiers):
		if symbol == pyglet.window.key.D:
			if self.debug == False:
				self.debug = True
			else:
				self.debug = False
		if symbol == pyglet.window.key.R:
			self.manager.go_to(Pymunk_Scene(self.window, self.level))
		if symbol == pyglet.window.key.ESCAPE:
			self.manager.go_to(Menu_Scene(self.window, self.level))
		if symbol == pyglet.window.key.C:
			self.camera.scale = 120
		if symbol == pyglet.window.key.X:
			self.camera.scale = 90
	def on_mouse_press(self, x, y, button, modifiers):
		pass
	def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
		self.level.on_mouse_drag(x, y, dx, dy, buttons, modifiers)
	def on_mouse_release(self, x, y, button, modifiers):
		pass
	def on_mouse_motion(self, x, y, dx, dy):
		pass
	def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
		self.camera.scroll_zoom(scroll_y)


from simplui import *

class Menu_Scene(Scene):
	def __init__(self, window, level):
		super(Menu_Scene, self).__init__(window, level)
		self.screen_resolution 	= window.width,window.height
		self.window = window

		self.debug_batch 		= pyglet.graphics.Batch()
		self.normal_batch 		= pyglet.graphics.Batch()
		self.ui_batch 			= pyglet.graphics.Batch()

		# The common_group parent keeps groups from 
		# overlapping on accident. Silly Pyglet!
		common_group 			= pyglet.graphics.OrderedGroup(1) 
		self.ordered_group10	= pyglet.graphics.OrderedGroup(10, 	parent = common_group)
		self.ordered_group9 	= pyglet.graphics.OrderedGroup(9, 	parent = common_group)
		self.ordered_group8 	= pyglet.graphics.OrderedGroup(8, 	parent = common_group)
		self.ordered_group7		= pyglet.graphics.OrderedGroup(7, 	parent = common_group)
		self.ordered_group6		= pyglet.graphics.OrderedGroup(6, 	parent = common_group)
		self.ordered_group5		= pyglet.graphics.OrderedGroup(5, 	parent = common_group)
		self.ordered_group4		= pyglet.graphics.OrderedGroup(4, 	parent = common_group)
		self.ordered_group3 	= pyglet.graphics.OrderedGroup(3,	parent = common_group)
		self.ordered_group2		= pyglet.graphics.OrderedGroup(2, 	parent = common_group)
		self.ordered_group1		= pyglet.graphics.OrderedGroup(1, 	parent = common_group)

		glEnable(GL_BLEND)
		glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

		themes = [Theme('themes/game'), Theme('themes/pywidget')]
		theme = 0
		self.frame = Frame(themes[theme], w=window.width, h=window.height)
		# let the frame recieve events from the window
		window.push_handlers(self.frame)
		# create and add a second window

		buttons = []
		for i in range(6):
			if i == 0:
				buttons.append(Label('Select a level to play!'))
				#buttons.append(Checkbox('Game?', h=100))
			buttons.append(Button('Level '+str(i), action=self.load_level))

		self.dialogue = Dialogue('Level Select', x=(window.width//2) - 60, y=(self.window.height//2), 
			content = VLayout(w=50,children=buttons))

		self.frame.add( self.dialogue )

	def update(self, dt):
		pass
	def update_half(self, dt):
		pass
	def update_third(self, dt):
		pass
	def draw(self):
		glClearColor(.1,.1,.12,1)
		self.normal_batch.draw()
		self.debug_batch.draw()
		self.ui_batch.draw()
		self.frame.draw()
	def world_pos(self, x, y):
		pass
	def keyboard_input(self, dt):
		pass
	def on_key_press(self, symbol, modifiers):
		pass
	def on_key_release(self, symbol, modifiers):
		if symbol == pyglet.window.key.ESCAPE:
			pyglet.app.exit()
	def on_mouse_press(self, x, y, button, modifiers):
		pass
	def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
		pass
	def on_mouse_release(self, x, y, button, modifiers):
		pass
	def on_mouse_motion(self, x, y, dx, dy):
		pass
	def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
		pass

	def load_level(self, button):
		print('-----\nLoading: "'+button._get_text()+'"')

		self.window.pop_handlers()
		self.manager.go_to(Pymunk_Scene(self.window, GameLevel1()))


class SceneManager(object):
	def __init__(self, window, level):
		self.go_to(Menu_Scene(window, level))
	def go_to(self, scene):
		self.scene = scene
		self.scene.manager = self