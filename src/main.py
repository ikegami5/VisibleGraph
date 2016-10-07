#!/usr/bin/env python
# coding: utf-8

from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, qApp, QToolBar
from PyQt5.QtWidgets import QGraphicsScene, QStyleOptionGraphicsItem, QComboBox
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QVector2D, QPainter, QPen, QBrush, QColor
import sys, math, random, glob, os

class Vertex(QVector2D):
	def __init__(self, x, y):
		self.connectVertices = []
		super().__init__(x, y)

	def addEdge(self, toVertex):
		self.connectVertices.append(toVertex)

	def __repr__(self):
		return "(" + str(self.x()) + ", " + str(self.y()) + ")"

class Graph(object):
	def __init__(self, *vertices):
		self.vertices = list(vertices)

	def addEdge(self, vertex1, vertex2):
		self.vertices[vertex1].addEdge(self.vertices[vertex2])
		self.vertices[vertex2].addEdge(self.vertices[vertex1])

	def numOfVertices(self):
		return len(self.vertices)

	def repulsiveForces(self, kValue):
		disps = [QVector2D(0, 0) for i in range(self.numOfVertices())]
		for (i, vertex) in enumerate(self.vertices):
			for j in range(self.numOfVertices()):
				if i != j:
					differenceVector = QVector2D(vertex - self.vertices[j])
					if differenceVector.length() < 0.1:
						differenceVector.setX(random.random() - 0.5)
						differenceVector.setY(random.random() - 0.5)
					disps[i] += differenceVector * pow(kValue, 2) / pow(differenceVector.length(), 2) / 4
		return disps

	def attractiveForces(self, kValue):
		disps = [QVector2D(0, 0) for i in range(self.numOfVertices())]
		for (index, vertex) in enumerate(self.vertices):
			for connectVertex in vertex.connectVertices:
				differenceVector = QVector2D(connectVertex - vertex)
				disps[index] += differenceVector * differenceVector.length() / kValue
		return disps

	def displacement(self, kValue):
		disps = [i[0] + i[1] for i in zip(self.repulsiveForces(kValue), self.attractiveForces(kValue))]
		return disps

	def move(self, temperature, area):
		kValue = math.sqrt(area / self.numOfVertices())
		disps = self.displacement(kValue)
		for (disp, vertex) in zip(disps, self.vertices):
			dispLength = disp.length()
			vertex += (disp / dispLength) * min(dispLength, temperature)

	def __repr__(self):
		return str(self.vertices)

class MainWindow(QMainWindow):

	def __init__(self):
		super().__init__()
		self.graph = Graph()
		self.scene = QGraphicsScene(50, 50, 400, 400, self)
		self.scene.area = self.scene.width() * self.scene.height()
		self.moveCount = 1
		self.initUI()

	def paintEvent(self, event):
		painter = QPainter()
		painter.begin(self)
		black = QColor(0, 0, 0)
		pen = QPen(black)
		brush = QBrush(black, Qt.SolidPattern)
		option = QStyleOptionGraphicsItem()
		for vertex in self.graph.vertices:
			vertex.ellipse = self.scene.addEllipse(vertex.x() - 3, vertex.y() - 3, 6, 6, pen, brush)
			vertex.ellipse.paint(painter, option, self)
			for connectVertex in vertex.connectVertices:
				painter.drawLine(vertex.toPoint(), connectVertex.toPoint())
		painter.end()

	def move(self):
		self.graph.move(self.temperature(), self.scene.area)
		for vertex in self.graph.vertices:
			vertex.setX(max(50, min(50 + self.scene.width(), vertex.x())))
			vertex.setY(max(50, min(50 + self.scene.height(), vertex.y())))
		self.moveCount += 1
		self.update()

	def finalMove(self):
		while self.temperature() > 1:
			self.move()

	def temperature(self):
		return self.scene.width() / self.moveCount

	def readGraph(self):
		readingFile = str(self.selectBox.currentText())
		graphData = __import__("graphData." + readingFile, 
			globals(), locals(), ["vertexCount", "edges"], 0)
		vertexCount = graphData.vertexCount
		edges = graphData.edges
		vertices = []
		for i in range(vertexCount):
			x = 250 + 100 * math.cos((i / vertexCount) * (2 * math.pi))
			y = 250 + 100 * math.sin((i / vertexCount) * (2 * math.pi))
			vertices.append(Vertex(x, y))
		self.graph = Graph(*vertices)
		for (edge1, edge2) in edges:
			self.graph.addEdge(edge1, edge2)
		self.moveCount = 1
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

		finalMoveAction = QAction("finalMove", self)
		finalMoveAction.triggered.connect(self.finalMove)

		toolBar = QToolBar(self)
		self.addToolBar(Qt.RightToolBarArea, toolBar)
		toolBar.addAction(exitAction)
		toolBar.addAction(readGraphAction)
		toolBar.addAction(moveAction)
		toolBar.addAction(finalMoveAction)

		self.selectBox = QComboBox(self)
		fileList = [os.path.basename(fileName) for fileName in glob.glob("./graphData/*.py")]
		fileList.remove("__init__.py")
		for index, file in enumerate(fileList):
			self.selectBox.insertItem(index, file[:-3])
		
		self.setGeometry(700, 100, 600, 500)
		self.setWindowTitle("visibleGraph")
		self.show()

if __name__ == '__main__':
	app = QApplication(sys.argv)
	mainWindow = MainWindow()
	sys.exit(app.exec_())

