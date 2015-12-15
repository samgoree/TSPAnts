# antColonyOpt.py
# Uses Ant Colony Optmization to solve a given TSP instance from argv[1], I used datasets from http://www.math.uwaterloo.ca/tsp/world/countries.html
# Based on "Ant Colony System: A Cooperative Learning Approach to the Traveling Salesman Problem" by Marco Dorigo and Luca Maria Gambardella from IEEE Transactions on Evolutionary Computation, Vol 1, no 1 April 1997 (http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.474.2440&rep=rep1&type=pdf)

import sys
import numpy as np
from Graph import *
from sklearn.preprocessing import normalize

# constants!
numiterations = 100
n = 0 # number of cities
m = 10 # number of ants
alpha = 0.1
beta = 2
rho = 0.1
q0 = 0.9
tau0 = 0

def main():
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
	# Do Dorigo and Gambaradella's algorithm
	for i in range(numiterations):
		#init ants
		ants = np.empty([m, n])
		ants[:,0] = np.random.choice(n, m, replace=False)
		for j in range(n-1):
			# state transition rule
			q = np.random.random_sample(m)
			rand = (q > q0) # true if the ant will move randomly this turn
			for k in range(m):
				ants[k,j+1] = selectNext(rand[k], ants[k,:j+1], g)
			# local pheromone updating rule
			np.vectorize(LUR)(g.edges)
		# global pheromone updating rule - find the best solution and make it more likely to succeed
		lengths = np.empty(len(ants))
		for j in range(len(ants)):
			lengths[j] = pathLength(ants[j], g)
		minPath = ants[np.argmin(lengths)]
		
	# return most popular path

# build a graph from the data
def initGraph(data):
	g = Graph()
	for i in range(len(data)/2):
		g.addNode(i)
		for j in range(i):
			g.addEdge(i, j, distance(float(data[i * 2]), float(data[i * 2 + 1]), float(data[j * 2]), float(data[j * 2 + 1])))
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
	if(actRandomly):
		choice = np.random.choice(edges, p=normalize(values, norm='l1')[0])
	else:
		choice = edges[np.argmax(values)]
	return choice.otherEndpointNumber(currentNode)
	
def pathLength(nodeNumbers, graph):
	length = 0
	for i in range(1, len(nodeNumbers)):
		length += graph.edgeLength(nodeNumbers[i-1], nodeNumbers[i])
	return length
	
# local updating rule
def LUR(edge):
	edge.popularity = (1 - rho) * edge.popularity + rho * tau0
	
# Global updating rule
#def GUR(edge, globalBestTour):
#	edge.popularity = (1 - alpha) * edge.popularity + alpha * 
		

# currently euclidian distance, can be modularized in the future for non-euclidian TSP
def distance(x1, y1, x2, y2): return np.sqrt((x2 - x1)**2 + (y2 - y1)**2)

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
	print(length)
	return length
		

main()
