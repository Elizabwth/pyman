import pyglet
import pymunk
from pymunk import Vec2d

import re

from math import sin,cos,tan,degrees,radians,sqrt
import contours

class Contour(object):
	def __init__(self, image_path):
		self.image_path = image_path
		img = pyglet.image.load(image_path)
		self.img_width, self.img_height = img.width, img.height

		tmp = contours.find_contours(image_path)
		self.layers = []
		
		for layer in tmp:
			layer.append(layer[0])
			self.layers.append(layer)

		for layer in self.layers:
			i = 0
			for point in layer:
				layer[i] = point[0]-(self.img_width/2)+.5, point[1]-(self.img_height/2)-.5
				i += 1

	def points(self):
		pts = []
		for layer in self.layers:
			for pt in layer:
				pts.append(pt)

		return pts

	def create_segments(self, space, radius, friction, elasticity):
		for layer in self.layers:
			i = 0
			for point in layer:

				seg = pymunk.Segment(space.static_body, point, layer[i-1], radius)
				seg.group = 2
				seg.elasticity = elasticity
				seg.friction = friction
				space.add(seg)

				i += 1

	def create_polys(self, space, friction, elasticity):
		shapes = contours.find_contours(self.image_path)
		for shape in shapes:
			i = 0
			for point in shape:
				shape[i] = point[0]-(self.img_width/2)+.5, point[1]-(self.img_height/2)-.5
				i += 1

		for shape in shapes:
			tris = pymunk.util.triangulate(shape)
			for tri in tris:
				print tri
				poly = pymunk.Poly(space.static_body, tri)
				poly.group = 2
				poly.elasticity = elasticity
				poly.friction = friction
				space.add(poly)




if __name__ == '__main__':
	pass