import utils
import math
from pyglet.gl import *

import pymunk
from pymunk import Vec2d
import pyglet_util
import geometry


def find_loops(point_dict):
	points = point_dict.values()

	padding = 100
	points = [(p1*padding, p2*padding) for (p1,p2) in points]
	#print points
	lines = []
	for i, point in enumerate(points):
		if (i < (len(points)-1)):
			lines.append((point, points[i+1]))

	intersection_indices = []
	intersection_points = []
	intersections = {}

	for a, lineA in enumerate(lines):
		for b, lineB in enumerate(reversed(lines)):
			intersection = geometry.calculateIntersectPoint(lineA[0], lineA[1], 
												   			lineB[0], lineB[1])
			if intersection != None and (lineA != lineB):
				#print intersection, a, len(lines)-b-1
				# if the geometry library intersection method finds 
				# an intersection which is one of the points in the original
				# list/dictionary of points, ignore it
				point_not_found = True
				if (intersection[0],intersection[1]) in points:
					point_not_found = False
				# if the geometry library intersection method finds 
				# an intersection which was already found, ignore it
				intersection_not_found = True
				if intersection in intersection_points:
					intersection_not_found = False

				# don't bother adding loops within loops
				intersection_within_not_found = True
				for idx in intersection_indices:
					if a > idx[0] and len(lines)-b-1 < idx[1] and a < len(lines)-b-1:
						print idx, a, len(lines)-b-1
						intersection_within_not_found = False

				if point_not_found and intersection_not_found and intersection_within_not_found:

					intersection_indices.append((a,len(lines)-b-1))
					intersection_points.append(intersection)

					intersections[(a,len(lines)-b-1)] = [intersection[0]/padding, intersection[1]/padding]

	print intersections
	return intersections

def find_normals(point_dict, scene, radius=120):
	new_dict = {}

	points = point_dict.values()
	for i, point in enumerate(points):
		if point == points[0] or point == points[-1]:
			# start and end points
			scene.debug_batch.add(2, GL_LINES, scene.ordered_group4,
							  ('v2f', (point[0],point[1],point[0],point[1]-radius)),
							  ('c3B', (55,255,85)*2))
			new_dict[i] = point[0], point[1]-radius
		else:
			angle1 = math.radians(utils.angle_between_points(point, points[i-1])+90)
			angle2 = math.radians(utils.angle_between_points(point, points[i+1])+90)
			delta = angle1-angle2-math.radians(180)
			# disable this and see what happens
			# yeah, i don't get it either...
			if delta < -3:
				delta += math.radians(360)

			normal_point = utils.point_on_circle(radius, 
											   	 angle1-delta/2, 
											   	 point)

			if normal_point[0] > points[0][0]:
				new_dict[i] = normal_point
			
			normal = (point[0], point[1], normal_point[0], normal_point[1])
			scene.debug_batch.add(2, GL_LINES, scene.ordered_group4,
							  ('v2f', normal),
							  ('c3B', (25,255,55)*2))
			scene.debug_batch.add(1, GL_POINTS, scene.ordered_group4,
							  ('v2f', (normal_point[0],normal_point[1])),
							  ('c3B', (95,95,255)))
		scene.debug_batch.add(1, GL_POINTS, scene.ordered_group4,
							  ('v2f', (point[0],point[1])),
							  ('c3B', (255,255,255)))
	return new_dict

def remove_loops(point_dict, scene):
	intersections = find_loops(point_dict)
	keys 		  = intersections.keys()
	values 		  = intersections.values()

	#print keys

	while len(keys) > 0:
		# remove first loop(s)
		skip = False
		for i in range(keys[0][1]-keys[0][0]):
			# check if the key actually exists within the dict
			if keys[0][0]+i+1 in point_dict:
				point_dict.pop(keys[0][0]+i+1)
			else: 
				skip = True
		# if the key exists, remove it and add a point at the intersection
		if not skip:
			delta = (keys[0][1]-keys[0][0])/2
			point_dict[keys[0][0]+delta] = intersections[keys[0]]
			# rebuild
			intersections.pop(keys[0])
			keys.pop(0)
		# if it doesn't, remove it from the keys
		else:
			keys.pop(0)

	l = []
	for point in point_dict.values():
		l.append(point[0])
		l.append(point[1])

	scene.debug_batch.add_indexed(len(l)/2, GL_LINES, scene.ordered_group5,
						  pyglet_util.calc_line_index(len(l)/2),
						  ('v2f', l),
						  ('c3B', (255,55,85)*(len(l)/2)))


class Generate(object):
	def __init__(self, points):
		self.points = points

		# make a dictionary or something of each point in the starting line
		# containing the point and its index
		# from each successive line, store its point and index like the first
		# after removing the loops found (by stepping through each successive line 
		# until no more loops exist [ex: find the first intersection, remove those
		# points inbetween, then use the new line without the loop we just got rid of
		# to find the next loop, then remove that, etc...])
		# all the while keeping track of edges that will connect each successing loop
		# by using the indices i recorded

	def find_normal(self, line1, line2, radius):
		## find individual normals from a pair of lines
		pass
	def find_edge_loop(self, points):
		## find the next edge loop using
		## find_normal() on each line
		## return a dictionary of the edgeloop's points
		## as well as their indicies
		## either {index:point} or {point:index}
		pass
	def find_downward_lines(self, lines):
		## construct downward lines which will connect each loop
		## using the point's index stored in the dictionary
		pass

	# don't use this, make a singular method
	def find_normal_lines(self, points, radius, current_pass):
		working_line = []
		i = 0
		for point in points:
			if point == points[0] or point == points[-1]:
				# start and end points
				self.scene.debug_batch.add(2, GL_LINES, self.scene.ordered_group4,
								  ('v2f', (point[0],point[1],point[0],point[1]-radius)),
								  ('c3B', (55,255,85)*2))
				working_line.append((point[0],point[1]-radius))
			else:

				angle1 = math.radians(utils.angle_between_points(point, points[i-1])+90)
				angle2 = math.radians(utils.angle_between_points(point, points[i+1])+90)
		
				delta = angle1-angle2-math.radians(180)
		
				# disable this and see what happens
				# yeah, i don't get it either...
				if delta < -3:
					delta += math.radians(360)

				new_step_point = utils.point_on_circle(radius, 
												   	   angle1-delta/2, 
												   	   point)

				working_line.append(new_step_point) # actual appending
				
				normal = (point[0], point[1], new_step_point[0], new_step_point[1])
							
	
				self.scene.debug_batch.add(2, GL_LINES, self.scene.ordered_group4,
								  ('v2f', normal),
								  ('c3B', (25,255,55)*2))

				self.scene.debug_batch.add(1, GL_POINTS, self.scene.ordered_group4,
								  ('v2f', (new_step_point[0],new_step_point[1])),
								  ('c3B', (95,95,255)))
	
			self.scene.debug_batch.add(1, GL_POINTS, self.scene.ordered_group4,
								  ('v2f', (point[0],point[1])),
								  ('c3B', (255,255,255)))

			i += 1
		
		l = []
		for point in working_line:
			l.append(point[0])
			l.append(point[1])

		'''
		#self.scene.debug_batch.add_indexed(len(l)/2, GL_LINES, self.scene.ordered_group5,
		#					  pyglet_util.calc_line_index(len(l)/2),
		#					  ('v2f', l),
		#					  ('c3B', (25,255,255)*(len(l)/2)))
		'''

		print working_line

		return working_line

'''
class GenerateMesh(object):
	def __init__(self, scene, points):
		self.scene = scene
		self.points = points

		self.pass_dict = {0:points}

		radius = 2
		for ps in xrange(8):
			if ps+1 not in self.pass_dict.keys():
				self.pass_dict[ps+1] = []

			self.pass_dict[ps+1] = self.find_normal_lines(self.pass_dict[ps], radius, ps)

			# should merge close vertices first
			self.pass_dict[ps+1] = self.cleanup(self.pass_dict[ps+1], ps)

			radius += radius/1.5

	def find_normal_lines(self, points, radius, current_pass):
		working_line = []
		i = 0
		for point in points:
			if point == points[0] or point == points[-1]:
				# start and end points
				self.scene.debug_batch.add(2, GL_LINES, self.scene.ordered_group4,
								  ('v2f', (point[0],point[1],point[0],point[1]-radius)),
								  ('c3B', (55,255,85)*2))
				working_line.append((point[0],point[1]-radius))
			else:

				angle1 = math.radians(utils.angle_between_points(point, points[i-1])+90)
				angle2 = math.radians(utils.angle_between_points(point, points[i+1])+90)
		
				delta = angle1-angle2-math.radians(180)
		
				# disable this and see what happens
				# yeah, i don't get it either...
				if delta < -3:
					delta += math.radians(360)

				new_step_point = utils.point_on_circle(radius, 
												   	   angle1-delta/2, 
												   	   point)

				if new_step_point[0] > 15 and new_step_point[0] < self.pass_dict[0][-1][0]:
					working_line.append(new_step_point) # actual appending

				elif new_step_point[0] > self.pass_dict[0][-1][0]:
					new_step_point = (self.pass_dict[0][-1][0], self.pass_dict[0][-1][1])
				else:
					new_step_point = working_line[0]
				
				normal = (point[0], point[1], new_step_point[0], new_step_point[1])
							
	
				self.scene.debug_batch.add(2, GL_LINES, self.scene.ordered_group4,
								  ('v2f', normal),
								  ('c3B', (25,255,55)*2))

				self.scene.debug_batch.add(1, GL_POINTS, self.scene.ordered_group4,
								  ('v2f', (new_step_point[0],new_step_point[1])),
								  ('c3B', (95,95,255)))
	
			self.scene.debug_batch.add(1, GL_POINTS, self.scene.ordered_group4,
								  ('v2f', (point[0],point[1])),
								  ('c3B', (255,255,255)))

			i += 1
		
		l = []
		for point in working_line:
			l.append(point[0])
			l.append(point[1])


		self.scene.debug_batch.add_indexed(len(l)/2, GL_LINES, self.scene.ordered_group5,
							  pyglet_util.calc_line_index(len(l)/2),
							  ('v2f', l),
							  ('c3B', (25,255,255)*(len(l)/2)))


		print working_line

		return working_line

	def cleanup(self, cur_line, current_pass):

		padding = 500

		prev_line = self.pass_dict[current_pass]

		for i, point in enumerate(cur_line):

			cur_line[i] = [point[0]*padding, point[1]*padding]

		lines = []
		for i in range(len(cur_line)):
			if i != 0:
				lines.append((cur_line[i-1],cur_line[i]))
		found_indces = []
		found_intersections = []
	
		inverse = len(lines)
	
		idx_a = 0
		for line1 in lines:
			idx_b = 0
			for line2 in reversed(lines):
				if line1 != line2:
					intersection = calculateIntersectPoint(line1[0], line1[1], 
														   line2[0], line2[1])
					if intersection != None:

						not_found = True
						for a,b in found_indces:
							if idx_a > a and (inverse-idx_b) < b:
								not_found = False
								break
							else:
								not_found = True
								break
							
						if not_found:
							found_intersections.append(intersection)
							found_indces.append((idx_a,inverse-idx_b-1))

						#print found_indces
						for idx1 in found_indces:
							i = 0
							for idx2 in found_indces:
								if (idx1[0],idx1[1]) == (idx2[1],idx2[0]):
									found_intersections.pop(i)
									found_indces.pop(i)
								i += 1
						#print found_indces
	
				idx_b += 1
			idx_a += 1


		print found_indces
		for idx1 in found_indces:
			i = 0
			for idx2 in found_indces:
				if (idx1[0],idx1[1]) == (idx2[1],idx2[0]):
					found_intersections.pop(i)
					found_indces.pop(i)
				i += 1
		print found_indces



		inv_padding = 0
		for i, intersection in enumerate(found_intersections):
			#if ((i)%2) == 0:
			a,b = found_indces[i]
			cur_line[a+1-inv_padding:b+1-inv_padding] = [(intersection[0], intersection[1])]
			inv_padding += b-a-1

		for i, point in enumerate(cur_line):
			cur_line[i] = [point[0]/padding, point[1]/padding]
		
		l = []
		for point in cur_line:
			l.append(point[0])
			l.append(point[1])

		self.scene.debug_batch.add_indexed(len(l)/2, GL_LINES, self.scene.ordered_group10,
							  pyglet_util.calc_line_index(len(l)/2),
							  ('v2f', l),
							  ('c3B', (255,55,55)*(len(l)/2)))
		
		return cur_line
'''

POINTS = [(0,0),(10,0),(10,0),(20,0),(20,0),(15,10),(15,10),(15,-10)]

if __name__ == '__main__':
	print remove_loops(POINTS)