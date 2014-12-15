from __future__ import division
import pyglet
import pymunk

from math import sin,cos,tan,degrees,sqrt,atan2,radians

def midpoint(a, b):
	return ((a[0]+b[0])/2.0,(a[1]+b[1])/2.0)
def distance(a, b):
	return sqrt(((b[0]-a[0])**2.0)+((b[1]-a[1])**2.0))

def weighted_average(c, d, w):
	return ((c * (w-1)) + d) / w

def point_on_circle(radius, angle, position):
	x = radius*cos(angle) + position[0]
	y = radius*sin(angle) + position[1]
	return (x,y)

def angle_between_points(a, b):
	xDiff = b[0]-a[0]
	yDiff = b[1]-a[1]
	#print(atan2(yDiff,xDiff))
	return degrees(atan2(yDiff,xDiff))

if __name__ == '__main__':
	print(midpoint((100,100),(0,0)))
	print(distance((0,0),(100,100)))