"""

Grid based Dijkstra planning

author: Atsushi Sakai(@Atsushi_twi)

"""

import math
import numpy as np
import time
# Dilation of the map scipy
from scipy.ndimage import binary_dilation

show_animation = False


class Dijkstra:

	def __init__(self, obstacle_map, robot_radius, obstacle = 1):
		"""
		Initialize map for a star planning

		ox: x position list of Obstacles [m]
		oy: y position list of Obstacles [m]
		resolution: grid resolution [m]
		rr: robot radius[m]
		"""

		self.min_x = None
		self.min_y = None
		self.max_x = None
		self.max_y = None
		self.x_width = None
		self.y_width = None
		self.obstacle_map = None

		self.robot_radius = robot_radius
		self.obstacle_map = obstacle_map.astype(bool)
		self.motion = self.get_motion_model()
		if obstacle == 1:
			self.obstacle_map = np.logical_not(self.obstacle_map)
		ox, oy = obstacle_map.nonzero()
		self.min_x = 0
		self.min_y = 0
		self.max_x = round(max(ox))
		self.max_y = round(max(oy))


		self.x_width = round((self.max_x - self.min_x))
		self.y_width = round((self.max_y - self.min_y))


	class Node:
		def __init__(self, x, y, cost, parent_index):
			self.x = x  # index of grid
			self.y = y  # index of grid
			self.cost = cost
			self.parent_index = parent_index  # index of previous Node

		def __str__(self):
			return str(self.x) + "," + str(self.y) + "," + str(
				self.cost) + "," + str(self.parent_index)

	def planning(self, start_node, goal_node, timeout = 10):
		"""
		dijkstra path search

		input:
			s_x: start x position [m]
			s_y: start y position [m]
			gx: goal x position [m]
			gx: goal x position [m]

		output:
			rx: x position list of the final path
			ry: y position list of the final path
		"""

		start_time = time.time()

		start_node = self.Node(self.calc_xy_index(start_node[0], self.min_x),
							   self.calc_xy_index(start_node[1], self.min_y), 0.0, -1)
		goal_node = self.Node(self.calc_xy_index(goal_node[0], self.min_x),
							  self.calc_xy_index(goal_node[1], self.min_y), 0.0, -1)

		open_set, closed_set = dict(), dict()
		open_set[self.calc_index(start_node)] = start_node

		while True:
			if not open_set:
				print("Cannot find path")
				return None
			c_id = min(open_set, key=lambda o: open_set[o].cost)
			current = open_set[c_id]


			if current.x == goal_node.x and current.y == goal_node.y:
				print("Find goal")
				goal_node.parent_index = current.parent_index
				goal_node.cost = current.cost
				break

			# Remove the item from the open set
			del open_set[c_id]

			# Add it to the closed set
			closed_set[c_id] = current

			# expand search grid based on motion model
			for move_x, move_y, move_cost in self.motion:
				node = self.Node(current.x + move_x,
								 current.y + move_y,
								 current.cost + move_cost, c_id)
				n_id = self.calc_index(node)

				if n_id in closed_set:
					continue

				if not self.verify_node(node):
					continue

				if n_id not in open_set:
					open_set[n_id] = node  # Discover a new node
				else:
					if open_set[n_id].cost >= node.cost:
						# This path is the best until now. record it!
						open_set[n_id] = node

			if time.time() - start_time > timeout:
				print("Timeout")
				return None

		rx,ry = self.calc_final_path(goal_node, closed_set)

		# Return as np array of two columns

		path = np.zeros((len(rx), 2))
		path[:, 0] = rx
		path[:, 1] = ry


		return path

	def calc_final_path(self, goal_node, closed_set):
		# generate final course
		rx, ry = [self.calc_position(goal_node.x, self.min_x)], [
			self.calc_position(goal_node.y, self.min_y)]
		parent_index = goal_node.parent_index
		while parent_index != -1:
			n = closed_set[parent_index]
			rx.append(self.calc_position(n.x, self.min_x))
			ry.append(self.calc_position(n.y, self.min_y))
			parent_index = n.parent_index

		return rx, ry

	def calc_position(self, index, minp):
		pos = index + minp
		return pos

	def calc_xy_index(self, position, minp):
		return round((position - minp))

	def calc_index(self, node):
		return (node.y - self.min_y) * self.x_width + (node.x - self.min_x)

	def verify_node(self, node):
		px = self.calc_position(node.x, self.min_x)
		py = self.calc_position(node.y, self.min_y)

		if px < self.min_x:
			return False
		if py < self.min_y:
			return False
		if px >= self.max_x:
			return False
		if py >= self.max_y:
			return False

		if self.obstacle_map[node.x][node.y]:
			return False

		return True

	def calc_obstacle_map(self, ox, oy):

		self.min_x = round(min(ox))
		self.min_y = round(min(oy))
		self.max_x = round(max(ox))
		self.max_y = round(max(oy))
		print("min_x:", self.min_x)
		print("min_y:", self.min_y)
		print("max_x:", self.max_x)
		print("max_y:", self.max_y)

		self.x_width = round((self.max_x - self.min_x))
		self.y_width = round((self.max_y - self.min_y))
		print("x_width:", self.x_width)
		print("y_width:", self.y_width)

		# obstacle map generation
		self.obstacle_map = [[False for _ in range(self.y_width)]
							 for _ in range(self.x_width)]


	@staticmethod
	def get_motion_model():
		# dx, dy, cost
		motion = [[1, 0, 1],
				  [0, 1, 1],
				  [-1, 0, 1],
				  [0, -1, 1],
				  [-1, -1, math.sqrt(2)],
				  [-1, 1, math.sqrt(2)],
				  [1, -1, math.sqrt(2)],
				  [1, 1, math.sqrt(2)]]

		return motion


def reduce_path_douglas_peucker(path, nav_map):

	""" Reduce the path using the Douglas-Peucker algorithm """

	from scipy.spatial import distance

	def perpendicular_distance(point, start, end):
		if np.array_equal(start, end):
			return distance.euclidean(point, start)
		else:
			num = abs((end[1] - start[1]) * point[0] - (end[0] - start[0]) * point[1] + end[0] * start[1] - end[1] * start[0])
			den = math.sqrt((end[1] - start[1])**2 + (end[0] - start[0])**2)
			return num / den

	def douglas_peucker(points, epsilon):
		if len(points) < 3:
			return points

		start = points[0]
		end = points[-1]

		max_dist = 0.0
		index = 0
		for i in range(1, len(points) - 1):
			dist = perpendicular_distance(points[i], start, end)
			if dist > max_dist:
				index = i
				max_dist = dist

		if max_dist > epsilon:
			left = douglas_peucker(points[:index + 1], epsilon)
			right = douglas_peucker(points[index:], epsilon)

			return np.vstack((left[:-1], right))
		else:
			return np.array([start, end])

	epsilon = 1.0  # Tolerance value, can be adjusted
	reduced_path = douglas_peucker(path, epsilon)

	return reduced_path

def reduce_path_bresenham(path, nav_map):

	""" Reduce the path by removing unnecessary waypoints if between two waypoints there is a straight line without obstacles """

	def is_line_free_bressen(p1, p2, nav_map):
		def bresenham(x0, y0, x1, y1):
			# yields integer coordinates on the line from (x0,y0) to (x1,y1)
			x0 = int(round(x0))
			y0 = int(round(y0))
			x1 = int(round(x1))
			y1 = int(round(y1))
			dx = abs(x1 - x0)
			dy = abs(y1 - y0)
			sx = 1 if x0 < x1 else -1
			sy = 1 if y0 < y1 else -1
			err = dx - dy
			x, y = x0, y0
			while True:
				yield x, y
				if x == x1 and y == y1:
					break
				e2 = 2 * err
				if e2 > -dy:
					err -= dy
					x += sx
				if e2 < dx:
					err += dx
					y += sy

		# ensure map is indexable as nav_map[row, col] -> nav_map[y, x]
		max_y, max_x = nav_map.shape
		x1, y1 = p1
		x2, y2 = p2

		for xi, yi in bresenham(x1, y1, x2, y2):
			# bounds check
			if xi < 0 or yi < 0 or xi >= max_x or yi >= max_y:
				# Out of bounds considered blocked
				return False
			# nav_map is expected to have 1 for obstacle
			if nav_map[yi, xi] == 1:
				return False

		return True
	
	# First and last points of the path
	index_i = 0
	index_f = len(path) - 1
	p1 = path[index_i]

	# New path will contain the reduced path from start to end
	new_path = [p1]
	N = len(path)
	if N <= 2:
		return np.asarray(path)

	# We'll use a greedy approach but find the farthest reachable index using binary search
	current_idx = 0

	while current_idx < N - 1:
		# binary search for farthest reachable index between (current_idx+1) .. (N-1)
		lo = current_idx + 1
		hi = N - 1
		best = lo
		while lo <= hi:
			mid = (lo + hi) // 2
			if is_line_free_bressen(path[current_idx], path[mid], nav_map):
				best = mid
				lo = mid + 1
			else:
				hi = mid - 1

		# If best didn't advance, force to next point to avoid infinite loops
		if best == current_idx:
			best = current_idx + 1

		new_path.append(path[best])
		current_idx = best

	return np.asarray(new_path)



	
def is_line_free(p1, p2, nav_map):
	""" Check if the line between two points is free of obstacles """

	# Get the coordinates of the line
	x1, y1 = p1
	x2, y2 = p2


	# Get the x and y coordinates of the line
	dx = x2 - x1
	dy = y2 - y1

	dt = 1000

	# Get the step size
	step_x = dx / dt
	step_y = dy / dt

	# Loop through the steps

	for t in range(dt):
		x = x1 + t * step_x
		y = y1 + t * step_y

		# Check if the point is inside an obstacle
		if nav_map[int(x), int(y)] == 1: # or nav_map[int(np.ceil(x)), int(np.ceil(y))] == 1:# or nav_map[int(np.ceil(x)), int(np.floor(y))] or nav_map[int(np.floor(x)), int(np.ceil(y))]: 
			return False
		
	return True

def is_line_free_new(p1, p2, nav_map):
    x1, y1 = map(int, map(round, p1))
    x2, y2 = map(int, map(round, p2))

    dx = abs(x2 - x1)
    dy = -abs(y2 - y1)
    sx = 1 if x1 < x2 else -1
    sy = 1 if y1 < y2 else -1
    err = dx + dy

    while True:
        # ojo al orden: nav_map[fila, columna] = nav_map[y, x]
        if not (0 <= y1 < nav_map.shape[0] and 0 <= x1 < nav_map.shape[1]):
            return False
        if nav_map[y1, x1]:   # celda ocupada
            return False
        if x1 == x2 and y1 == y2:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x1 += sx
        if e2 <= dx:
            err += dx
            y1 += sy
    return True


def reduce_path_new(path, nav_map):
    path = np.asarray(path)
    n = len(path)
    if n <= 2:
        return path

    new_path = [path[0]]
    i = 0
    while i < n - 1:
        progressed = False
        # probar del final hacia atrás
        for j in range(n - 1, i, -1):
            if is_line_free_new(path[i], path[j], nav_map):
                new_path.append(path[j])
                i = j
                progressed = True
                break
        if not progressed:
            # no hay línea directa: avanzar al siguiente para garantizar progreso
            new_path.append(path[i + 1])
            i += 1
    return np.asarray(new_path)

def reduce_path(path, nav_map):
	""" Reduce the path by removing unnecessary waypoints if between two waypoints there is a straight line without obstacles """

	# First and last points of the path
	index_i = 0
	index_f = len(path) - 1
	p1 = path[index_i]

	# New path
	new_path = [p1]
	path_completed = False
	# Loop through p1 to the furthest point in the path that is free of obstacles from p1

	while not path_completed:


		# Loop inverse from the end of the path to the next point of index index_i
		for i in reversed(range(index_i, len(path))):
			p2 = path[i] # Take the point

			# Check if the point is the next point of index index_i

			if index_i == i and len(new_path) > 1:
				p2 = path[i+1]
				new_path.append(p2)
				index_i = i
				p1 = p2
				break

			# Check if the line between p1 and p2 is free of obstacles
			elif is_line_free(p1, p2, nav_map):
				# If it is free, then we can remove p2
				new_path.append(p2)
				index_i = i
				p1 = p2

				# When p1 is the last point, then the path is completed
				if np.all(p1 == path[-1]):
					path_completed = True

				break

	
	# Return the new path reversed
	return np.asarray(new_path)[::-1]



def main():
	print(__file__ + " start!!")

	import numpy as np

	init_node = (7, 69)
	goal_node = (80, 209)
	#goal_node = (52, 73)
	# map_grid = np.loadtxt('/home/samuel/ASV_loyola_us_repo/ASV_Loyola_US/asv_workspace/mapas/othermap.txt')
	

	map_grid = np.loadtxt('mapas/Alamillo95x216plantilla.csv', delimiter=" ").astype(int)

	# Dilation of the map
	dilated_map = binary_dilation(map_grid, np.ones((3, 3)))
	
	# set obstacle positions
	ox, oy = np.where(map_grid == 1)

	dijkstra = Dijkstra(dilated_map, 1)
	path = dijkstra.planning(init_node, goal_node)

	if path is not None:
		refined_path = reduce_path(path, dilated_map)
		print(refined_path)


if __name__ == '__main__':
	main()