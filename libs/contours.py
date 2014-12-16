from PIL import Image
from cv2  import findContours,RETR_CCOMP,RETR_TREE,CHAIN_APPROX_SIMPLE,convexHull,boundingRect
from numpy import array as numpy_array

import pyglet
import pymunk

import os
import sys
os.chdir(os.path.dirname(sys.argv[0]))

def img2np(img='data.bmp'):
	bmp = Image.open(img)
	return numpy_array(bmp)

def find_contours(img):
	data = img2np(img)
	# image file to numpy array.
	# it might be useful to see that:
	# width = len(data)
	# height = len(data[0])
	width = len(data[0])
	height = len(data)

	contours, heirarchy = findContours(data, RETR_TREE,CHAIN_APPROX_SIMPLE)

	layers = []
	i = 0
	for contour in contours:
		layers.append([])
		for data in contour:
			# subtract y value by height
			# to flip the y axis since
			# PIL reads the image from the
			# top left while pyglet draws
			# from the bottom left
			layers[i].append((data[0][0],height-data[0][1]))
		i += 1
	return layers

if __name__ == '__main__':
	''' # reduced poly
	tmp = find_contours('test.bmp')
	layers = []
	for layer in tmp:
		layer = pymunk.util.reduce_poly(layer, tolerance=150)
		layers.append(layer)
		print(len(layer))
	'''
	# actual poly
	layers = find_contours('test.bmp')

	window = pyglet.window.Window(width=640, height=500)
	@window.event
	def on_draw():
		window.clear()
		''' lines
		for layer in layers:
			p = []
			for point in layer:
				p.append(point[0])
				p.append(point[1])
			pyglet.graphics.draw(len(p)//2, pyglet.gl.GL_LINE_LOOP,
				('v2f', p))
		'''

		for layer in layers:
			tris = pymunk.util.triangulate(layer)
			t = []
			for tri in tris:
				t.append(tri[0][0]*2)
				t.append(tri[0][1]*2)
				t.append(tri[1][0]*2)
				t.append(tri[1][1]*2)
				t.append(tri[1][0]*2)
				t.append(tri[1][1]*2)
				t.append(tri[2][0]*2)
				t.append(tri[2][1]*2)
				t.append(tri[2][0]*2)
				t.append(tri[2][1]*2)
				t.append(tri[0][0]*2)
				t.append(tri[0][1]*2)
				pyglet.graphics.draw(len(t)//2, pyglet.gl.GL_LINES,
					('v2f', t))
		
	pyglet.clock.set_fps_limit(60)
	pyglet.app.run()