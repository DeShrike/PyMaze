import queue
import time 
import random
import pygame 
from Graphics import Graphics

WIDTH = 500
HEIGHT = 600

WAITING = "waiting"
BUILDING = "building"
SOLVING = "solving"

STATE = BUILDING

WHITE = (255, 255, 255)
GREEN = (0, 128, 0)
RED = (128, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
BLACK = (0, 0, 0)

XCELLS = 30
YCELLS = 40

graphics = Graphics()
graphics.init("Maze", (WIDTH, HEIGHT))

solver = None
builder = None
maze = None

#########################################################################
#########################################################################
#########################################################################

class Node():
	H = 0 # distance from goal (Manhattan distance)
	G = 0 # distance from start
	Parent = None
	x = 0
	y = 0

	def __init__(self, x, y):
		self.x = x
		self.y = y

	def F(self):
		return self.G + self.H

#########################################################################
#########################################################################
#########################################################################

class MazeSolver():
	maze = None
	start = None
	goal = None
	nodes = {}
	openList = []
	closedList = []
	currentPos = None
	tempSolution = None

	def __init__(self, maze, start, goal):
		self.maze = maze
		self.start = start
		self.goal = goal
		self.openList.append(start)

	def build_nodes(self):
		for i in range(0, XCELLS):
			for j in range(0, YCELLS):
				key = (i, j)
				if key in self.maze.grid:
					n = Node(i, j)
					n.H = self.manhattanDistance(self.goal, (i, j))
					n.G = 0
					self.nodes[key] = n

	def manhattanDistance(self, van, naar):
		return abs(van[0] - naar[0]) + abs(van[1] - naar[1])

	def getNeighbours(self, x, y):
		n = []
		key = (x, y)
		node = self.nodes[key]
		g = self.maze.grid[key]
		up = (x, y - 1)
		down = (x, y + 1)
		left = (x - 1, y)
		right = (x + 1, y)
		if up in self.nodes and g[0] == False:
			n.append(up)
		if down in self.nodes and g[2] == False:
			n.append(down)
		if left in self.nodes and g[3] == False:
			n.append(left)
		if right in self.nodes and g[1] == False:
			n.append(right)
		return n

	def doStep(self):
		if len(self.openList) == 0:
			return True

		self.currentPos = self.openList[0]
		currentNode = self.nodes[self.currentPos]
		for n in self.openList:
			node = self.nodes[n]
			if node.F() <= currentNode.F() and node.H < currentNode.H:
				self.currentPos = n
				currentNode = node

		self.openList.remove(self.currentPos)
		self.closedList.append(self.currentPos)

		if self.currentPos == self.goal:
			self.getSolution()
			return True

		neighbours = self.getNeighbours(self.currentPos[0], self.currentPos[1])
		for n in neighbours:
			node = self.nodes[n]
			if n in self.closedList:
				continue
			moveCost = currentNode.G + self.manhattanDistance(self.currentPos, n)
			if moveCost < node.G or n not in self.openList:
				node.G = moveCost
				node.H = self.manhattanDistance(n, self.goal)
				node.Parent = currentNode
				if n not in self.openList:
					self.openList.append(n)

		self.buildTempSolution()
		return False

	def getSolution(self):
		path = []
		current = self.nodes[self.goal]
		while (current.x, current.y) != self.start:
			path.append((current.x, current.y))
			current = current.Parent
		path.reverse()
		self.maze.solution = path[:]

	def buildTempSolution(self):
		path = []
		current = self.nodes[self.currentPos]
		while current != None and (current.x, current.y) != self.start:
			path.append((current.x, current.y))
			current = current.Parent
		path.reverse()
		self.tempSolution = path[:]

#########################################################################
#########################################################################
#########################################################################

class Maze():
	offsetx = 10
	offsety = 10
	cellw = (WIDTH - (2 * offsetx)) / XCELLS
	cellh = (HEIGHT - (2 * offsety)) / YCELLS
	grid = {}
	solution = None

	def __init__(self):
		pass

	def draw(self, builder, solver):
		padding = 4
		for j in range(0, XCELLS):
			for i in range(0, YCELLS):
				if (j, i) in self.grid:
					g = self.grid[(j, i)]
					x1 = j * self.cellw + self.offsetx
					y1 = i * self.cellh + self.offsety
					x2 = j * self.cellw + self.cellw + self.offsetx
					y2 = i * self.cellh + self.cellh + self.offsety
					if g[0]:
						graphics.line(x1, y1, x2, y1, 1, WHITE)	
					if g[1]:
						graphics.line(x2, y1, x2, y2, 1, WHITE)	
					if g[2]:
						graphics.line(x2, y2, x1, y2, 1, WHITE)	
					if g[3]:
						graphics.line(x1, y2, x1, y1, 1, WHITE)
					# if (j, i) in q:
					#	graphics.rect(x1 + 3, y1 + 3, cellw - 3, cellh - 3, GREEN)
					if STATE == BUILDING:
						if builder.currentPos[0] == j and builder.currentPos[1] == i:
							graphics.rect(x1 + padding, y1 + padding, self.cellw - padding * 2, self.cellh - padding * 2, YELLOW)
					if STATE == SOLVING:
						if solver.currentPos[0] == j and solver.currentPos[1] == i:
							graphics.rect(x1 + padding, y1 + padding, self.cellw - padding * 2, self.cellh - padding * 2, YELLOW)
						if solver.tempSolution != None and (j, i) in solver.tempSolution:
							graphics.rect(x1 + padding, y1 + padding, self.cellw - padding * 2, self.cellh - padding * 2, RED)							
					if STATE == WAITING and self.solution != None:
						if (j, i) in self.solution:
							graphics.rect(x1 + padding, y1 + padding, self.cellw - padding * 2, self.cellh - padding * 2, GREEN)

#########################################################################
#########################################################################
#########################################################################

class MazeBuilder():

	currentPos = None
	q = []
	visited = []
	maze = None

	def __init__(self, maze):
		self.maze = maze

	def build_grid(self):
		for j in range(0, XCELLS):
			for i in range(0, YCELLS):
				g = [True, True, True, True]
				if i > 10 and i < 20 and j > 10 and j < 20:
					pass
				else:
					self.maze.grid[(j, i)] = g
		
		self.currentPos = (0, 0)
		self.q.append(self.currentPos)
		self.visited.append(self.currentPos)

	def go_up(self):
		self.maze.grid[self.currentPos][0] = False
		self.currentPos = (self.currentPos[0], self.currentPos[1] - 1)
		self.maze.grid[self.currentPos][2] = False
		self.visited.append(self.currentPos)
		self.q.append(self.currentPos)

	def go_right(self):
		self.maze.grid[self.currentPos][1] = False
		self.currentPos = (self.currentPos[0] + 1, self.currentPos[1])
		self.maze.grid[self.currentPos][3] = False
		self.visited.append(self.currentPos)
		self.q.append(self.currentPos)

	def go_down(self):
		self.maze.grid[self.currentPos][2] = False
		self.currentPos = (self.currentPos[0], self.currentPos[1] + 1)
		self.maze.grid[self.currentPos][0] = False
		self.visited.append(self.currentPos)
		self.q.append(self.currentPos)

	def go_left(self):
		self.maze.grid[self.currentPos][3] = False
		self.currentPos = (self.currentPos[0] - 1, self.currentPos[1])
		self.maze.grid[self.currentPos][1] = False
		self.visited.append(self.currentPos)
		self.q.append(self.currentPos)

	def doStep(self):
		if len(self.q) == 0:
			return True
		g = self.maze.grid[self.currentPos]
		sides = []
		if g[0]:
			newpos = (self.currentPos[0], self.currentPos[1] - 1)
			if newpos in self.maze.grid and newpos not in self.visited:
				sides.append(0)
		if g[1]:
			newpos = (self.currentPos[0] + 1, self.currentPos[1])
			if newpos in self.maze.grid and newpos not in self.visited:
				sides.append(1)
		if g[2]:
			newpos = (self.currentPos[0], self.currentPos[1] + 1)
			if newpos in self.maze.grid and newpos not in self.visited:
				sides.append(2)
		if g[3]:
			newpos = (self.currentPos[0] - 1, self.currentPos[1])
			if newpos in self.maze.grid and newpos not in self.visited:
				sides.append(3)

		if len(sides) == 0:
			self.currentPos = self.q.pop()
		else:
			s = random.choice(sides)
			if s == 0:
				self.go_up()
			if s == 1:
				self.go_right()
			if s == 2:
				self.go_down()
			if s == 3:
				self.go_left()

		return False

#########################################################################
#########################################################################
#########################################################################

def do_solve_step():
	global solver, STATE, builder
	if solver == None:
		solver = MazeSolver(maze, (XCELLS - 1, 0), (0, YCELLS - 1))
		solver.build_nodes()
	if solver.doStep():
		STATE = WAITING

def do_build_step():
	global solver, STATE, builder
	if builder == None:
		builder = MazeBuilder(maze)
		builder.build_grid()
	if builder.doStep():
		STATE = SOLVING

def run():
	global STATE, maze
	maze = Maze()
	STATE = BUILDING
	done = False
	while not done:
		done = graphics.queryQuit()
		graphics.fill(BLACK)

		if STATE == BUILDING:
			do_build_step()

		if STATE == SOLVING:
			do_solve_step()

		maze.draw(builder, solver)
		graphics.flip()

	graphics.quit()


if __name__ == "__main__":
	run()
