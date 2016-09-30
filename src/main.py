#!/usr/bin/env python
# coding: utf-8

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, qApp, QToolBar
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QVector2D, QPainter

class Node(QPoint):
	def __init__(self, x, y):
		self.connectNodes = []
		super().__init__(x, y)

	def addEdge(self, toNode):
		self.connectNodes.append(toNode)

	def power(self):
		kValue = 1
		normalLength = 50
		sumPower = QVector2D(0, 0);
		selfVector = QVector2D(self)
		for connectNode in self.connectNodes:
			connectNodeVector = QVector2D(connectNode)
			subtractVector = connectNodeVector - selfVector
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
	def __init__(self, *nodes):
		self.nodes = list(nodes)

	def addEdge(self, node1, node2):
		self.nodes[node1].addEdge(self.nodes[node2])
		self.nodes[node2].addEdge(self.nodes[node1])

	def __repr__(self):
		return str(self.nodes)

class MainWindow(QMainWindow):

	def __init__(self, graph):
		super().__init__()
		self.graph = graph
		self.initUI()

	def paintEvent(self, event):
		painter = QPainter()
		painter.begin(self)
		for node in self.graph.nodes:
			painter.drawEllipse(node, 3, 3)
			for connectNode in node.connectNodes:
				painter.drawLine(node, connectNode)
		painter.end()

	def move(self):
		first = True
		for node in self.graph.nodes:
			if first:
				first = False
				continue
			node.move(node.power())
		self.update()

	def initUI(self):
		exitAction = QAction("Exit", self)
		exitAction.setShortcut("Ctrl+Q")
		exitAction.triggered.connect(qApp.quit)

		moveAction = QAction("Move", self)
		moveAction.setShortcut("Ctrl+R")
		moveAction.triggered.connect(self.move)

		toolBar = QToolBar(self)
		self.addToolBar(Qt.RightToolBarArea, toolBar)
		toolBar.addAction(exitAction)
		toolBar.addAction(moveAction)
		
		self.setGeometry(700, 100, 700, 500)
		self.setWindowTitle("visibleGraph")
		self.show()

if __name__ == '__main__':
	app = QApplication(sys.argv)
	nodes = [Node(x, y) for (x, y) in [(350, 300), (270, 270), (250, 230), (250, 300)]]
	graph = Graph(*nodes)
	for (edge1, edge2) in [(0, 1), (1, 2), (1, 3), (2, 3)]:
		graph.addEdge(edge1, edge2)
	mainWindow = MainWindow(graph)
	sys.exit(app.exec_())
