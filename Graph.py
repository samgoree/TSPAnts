# Graph.py
# Contains relevant classes for graph implementation

import sys
import numpy as np

# represents a graph node
class Node:

	edges = np.array([])
	name = -1
	
	def __init__(self, name, edges=[]):
		self.edges = edges
		self.name = name
	
	# ants can use this to figure out which paths they can take
	def otherEdges(self, edge):
		return np.remove(self.edges, edge)
	
	def addEdge(self, edge):
		self.edges = np.append(self.edges, edge)
		
	def __str__(self):
		return str(self.name)
		
	def __int__(self):
		return self.name

# represents a graph edge
class Edge:
	
	nodes = []
	name = -1
	length = 0
	popularity = 1 # a weight for how likely an ant is to choose this edge
	
	def __init__(self, name, endpoints, length):
		if len(endpoints) != 2:
			sys.stderr.write("Error: An edge can only go between two nodes in a graph.\n")
			sys.exit(1)
		else:
			self.nodes = endpoints
			self.name = name
			self.length = length
	def otherEndpointNumber(self, node):
		return int(self.nodes[1]) if node == self.nodes[0] else int(self.nodes[0])
	
	def __str__(self):
		return str(self.name)
	
# represents a graph
class Graph:
	edges = []
	nodes = {}
	
	def addNode(self, name):
		self.nodes[name] = Node(name)
		
	def addEdge(self, u, v, length):
		newEdge = Edge(str(u) + "-" + str(v), [self.nodes[u], self.nodes[v]], length)
		self.nodes[u].addEdge(newEdge)
		self.nodes[v].addEdge(newEdge)
		self.edges.append(newEdge)
	def __str__(self):
		return "Nodes: " + str(self.nodes) + "\nEdges: " + str(self.edges)
	
	def edgeLength(self, u, v):
		for e in self.edges:
			if self.nodes[u] in e.nodes and self.nodes[v] in e.nodes:
				return e.length
			elif u in e.nodes and v in e.nodes:
				return e.length
		return -1
	
	
	
	
	
	
	
	
