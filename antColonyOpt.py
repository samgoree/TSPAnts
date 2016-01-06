# antColonyOpt.py
# Sam Goree
# Uses Ant Colony Optmization to solve a given TSP instance from argv[1], I used datasets from http://www.math.uwaterloo.ca/tsp/world/countries.html
# Based on "Ant Colony System: A Cooperative Learning Approach to the Traveling Salesman Problem" by Marco Dorigo and Luca Maria Gambardella from IEEE Transactions on Evolutionary Computation, Vol 1, no 1 April 1997 (http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.474.2440&rep=rep1&type=pdf)

import sys
import numpy as np
from Graph import *
from sklearn.preprocessing import normalize

# constants!
numiterations = 30
n = 0 # number of cities
m = 10 # number of ants
alpha = 0.1 # see Dorigo and Gambardella for more information on these constants
beta = 2
rho = 0.1
q0 = 0.9
tau0 = 0 # will be set in main

scale = .001 # adjustment to scale down distances by - makes math easier to check by hand

SILENT = False

def main():
	if len(sys.argv) != 2:
		print("Enter exactly one file for data.")
		return
	# read the input file
	f = open(sys.argv[1])
	data = np.array([])
	for line in f:
		if line[0].isdigit():
			data = np.append(data, line.split()[1:])
	# initialize the graph
	g = initGraph(data)
	n = len(g.nodes)
	# find an initial approximation of the shortest path with the nearest neighbor method
	tau0 = 1/(n * nearestNeighbor(g))
	for e in g.edges:
		e.popularity = tau0
		e.popularityCache = tau0
	# Do Dorigo and Gambaradella's algorithm - see the paper for more details
	globalMinPath = []
	globalMinLength = sys.maxint
	for i in range(numiterations):
		if not SILENT: print("Iteration " + str(i))
		#init ants
		ants = np.empty([m, n])
		ants[:,0] = np.random.choice(n, m, replace=False)
		paths = []
		for i in range(m): paths.append([])
		for j in range(n-1):
			# apply state transition rule
			q = np.random.random_sample(m)
			rand = (q > q0) # true if the ant will move randomly this turn
			for k in range(m):
				ants[k,j+1] = selectNext(rand[k], ants[k,:j+1], g)
				paths[k].append(g.getEdge(ants[k,j],ants[k,j+1]))
				# local pheromone updating rule
				LUR(g.getEdge(ants[k,j],ants[k,j+1]))
			
		# global pheromone updating rule - find the best solution and make it more likely to succeed
		lengths = np.empty(len(ants))
		for j in range(len(ants)):
			lengths[j] = pathLength(ants[j], g)
		minLength = np.amin(lengths)
		minPath = paths[np.argmin(lengths)]
		# record the length if it's the best so far
		if minLength < globalMinLength: 
			globalMinLength = minLength
			globalMinPath = minPath
		partOfMinPath = np.empty([len(g.edges), 1])
		partOfMinPath.fill(False)
		for j in range(len(minPath)):
			partOfMinPath[g.getEdgeNumber(minPath[j])] = True
		# update the pheromones
		for j in range(len(g.edges)):
			g.edges[j].popularity = g.edges[j].popularityCache
			GUR(g.edges[j], partOfMinPath[j], minLength)
			g.edges[j].popularityCache = g.edges[j].popularity
		if not SILENT: print("minimum path length found this iteration: " + str(minLength))
	# return most popular path
	print(globalMinLength)
	for i in range(len(globalMinPath)):
		print(globalMinPath[i])
		if not SILENT: print(globalMinPath[i].popularity)

# build a graph from the data
def initGraph(data):
	g = Graph()
	for i in range(len(data)/2):
		g.addNode(i)
		for j in range(i):
			g.addEdge(i, j, distance(float(data[i * 2]) * scale, float(data[i * 2 + 1]) * scale, float(data[j * 2]) * scale, float(data[j * 2 + 1]) * scale))
	return g
	
# tells an ant where to go next
def selectNext(actRandomly, visitedNodes, graph):
	# argmax over edges from j-1th node to unvisited nodes (tau(edge) * mu(edge)^beta) if rand else S where S is a random distribution over those same values
	# get the "value" of each edge
	currentNode = graph.nodes[visitedNodes[len(visitedNodes)-1]]
	edges = currentNode.edges
	i = 0
	while i < len(edges):
		# if we've visisted any of the nodes at the other ends of edges, remove them
		if np.intersect1d(np.vectorize(int)(edges[i].nodes), visitedNodes) != []: 
			edges = np.delete(edges, i)
		else: i += 1
	values = np.vectorize(tau)(edges) * np.vectorize(mu)(edges) ** beta
	# a random choice will be distributed according to the relative distances and weights
	if(actRandomly):
		choice = np.random.choice(edges, p=normalize(values, norm='l1')[0])
	# a nonrandom choice will be the best according to the relative distances and weights
	else:
		choice = edges[np.argmax(values)]
	return choice.otherEndpointNumber(currentNode)
	
# used to measure the distance of a path by node numbers
def pathLength(nodeNumbers, graph):
	length = 0
	for i in range(1, len(nodeNumbers)):
		length += graph.edgeLength(nodeNumbers[i-1], nodeNumbers[i])
	return length
	
# local updating rule
def LUR(edge):
	edge.popularity = (1 - rho) * edge.popularity + rho * tau0
	
# Global updating rule - globalBestTour should be an array of booleans where the true values are part of the global best tour for this iteration
def GUR(edge, globalBestTour, length):
	edge.popularity = (1 - alpha) * edge.popularity + alpha * ((1/length) if globalBestTour else 0)
		

# currently euclidian distance, can be modularized in the future for non-euclidian TSP
def distance(x1, y1, x2, y2): return np.sqrt((x2 - x1)**2 + (y2 - y1)**2)

# used for vectorization - tau and mu are these things in the paper
def tau(edge):
	return edge.popularity
def mu(edge):
	return 1/edge.length

# Approximates the solution to TSP on a graph using the Nearest Neighbor method	
def nearestNeighbor(graph):
	length = 0
	visitedNodes = np.array([0])
	for i in range(len(graph.nodes)-1):
		currentNode = visitedNodes[len(visitedNodes)-1]
		edges = graph.nodes[currentNode].edges
		j = 0
		while j < len(edges):
			if np.intersect1d(np.vectorize(int)(edges[j].nodes), visitedNodes) != []: 
				edges = np.delete(edges, j)
			else: j+=1
		nextNodeIndex = np.argmax(np.vectorize(mu)(edges))
		visitedNodes = np.append(visitedNodes, edges[nextNodeIndex].otherEndpointNumber(visitedNodes[len(visitedNodes)-1]))
		length += edges[nextNodeIndex].length
	return length
		

main()
