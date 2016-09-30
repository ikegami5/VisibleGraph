#!/usr/bin/env python
# coding: utf-8

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, qApp, QToolBar
from PyQt5.QtWidgets import QGraphicsScene, QStyleOptionGraphicsItem
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QVector2D, QPainter, QPen, QBrush, QColor
from graphData.graph1 import vertexCount, edges
import math

class Vertex(QPoint):
	def __init__(self, x, y):
		self.connectVertices = []
		super().__init__(x, y)

	def addEdge(self, toVertex):
		self.connectVertices.append(toVertex)

	def power(self):
		kValue = 1
		normalLength = 50
		sumPower = QVector2D(0, 0);
		selfVector = QVector2D(self)
		for connectVertex in self.connectVertices:
			connectVertexVector = QVector2D(connectVertex)
			subtractVector = connectVertexVector - selfVector
			magnitude = kValue * (subtractVector.length() - normalLength)
			sumPower += (magnitude / subtractVector.length()) * subtractVector
		return sumPower

	def move(self, vector):
		selfVector = QVector2D(self)
		movedVector = selfVector + vector
		self.setX(movedVector.x())
		self.setY(movedVector.y())

	def __repr__(self):
		return "(" + str(self.x()) + ", " + str(self.y()) + ")"

class Graph():
	def __init__(self, *vertices):
		self.vertices = list(vertices)

	def addEdge(self, vertex1, vertex2):
		self.vertices[vertex1].addEdge(self.vertices[vertex2])
		self.vertices[vertex2].addEdge(self.vertices[vertex1])

	def numOfVertices(self):
		return len(self.vertices)

	def __repr__(self):
		return str(self.vertices)

class MainWindow(QMainWindow):

	def __init__(self):
		super().__init__()
		self.graph = Graph()
		self.scene = QGraphicsScene(100, 100, 300, 300, self)
		self.scene.area = 300 * 300
		self.initUI()

	def paintEvent(self, event):
		painter = QPainter()
		painter.begin(self)
		blue = QColor(0, 0, 255)
		pen = QPen(blue)
		brush = QBrush(blue, Qt.SolidPattern)
		option = QStyleOptionGraphicsItem()
		for vertex in self.graph.vertices:
			vertex.ellipse = self.scene.addEllipse(vertex.x() - 3, vertex.y() - 3, 6, 6, pen, brush)
			vertex.ellipse.paint(painter, option, self)
			for connectVertex in vertex.connectVertices:
				painter.drawLine(vertex, connectVertex)
		painter.end()

	def move(self):
		first = True
		for vertex in self.graph.vertices:
			if first:
				first = False
				continue
			vertex.move(vertex.power())
		self.update()

	def readGraph(self):
		vertices = []
		for i in range(vertexCount):
			x = 250 + 100 * math.cos((i / vertexCount) * (2 * math.pi))
			y = 250 + 100 * math.sin((i / vertexCount) * (2 * math.pi))
			vertices.append(Vertex(x, y))
		self.graph = Graph(*vertices)
		for (edge1, edge2) in edges:
			self.graph.addEdge(edge1, edge2)
		self.update()

	def initUI(self):
		exitAction = QAction("Exit", self)
		exitAction.setShortcut("Ctrl+Q")
		exitAction.triggered.connect(qApp.quit)

		readGraphAction = QAction("ReadGraph", self)
		readGraphAction.triggered.connect(self.readGraph)

		moveAction = QAction("Move", self)
		moveAction.setShortcut("Ctrl+R")
		moveAction.triggered.connect(self.move)

		toolBar = QToolBar(self)
		self.addToolBar(Qt.RightToolBarArea, toolBar)
		toolBar.addAction(exitAction)
		toolBar.addAction(readGraphAction)
		toolBar.addAction(moveAction)
		
		self.setGeometry(700, 100, 600, 500)
		self.setWindowTitle("visibleGraph")
		self.show()

if __name__ == '__main__':
	app = QApplication(sys.argv)
	mainWindow = MainWindow()
	sys.exit(app.exec_())
