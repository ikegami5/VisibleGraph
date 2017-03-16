#!/usr/bin/env python
# coding: utf-8

from PyQt5.QtWidgets import QGraphicsEllipseItem, QGraphicsLineItem, QPushButton
from PyQt5.QtWidgets import QStyleOptionGraphicsItem, QComboBox, QVBoxLayout
from PyQt5.QtWidgets import QDesktopWidget, QGraphicsScene, QGraphicsView, QHBoxLayout
from PyQt5.QtWidgets import QApplication, QWidget, qApp, QLineEdit, QLabel
from PyQt5.QtCore import QRectF, Qt, QLineF, QRect
from PyQt5.QtGui import QVector3D, QPen, QBrush, QVector2D, QPainter, QMatrix3x3
import os, math, sys, glob, random, numpy


class Vertex3D(QVector3D):

	def __init__(self, x, y, z):
		super().__init__(x, y, z)
		self.disp = QVector3D(0, 0, 0)
		self.edges = []
		self.circle = Vertex3DCircle(self)
		self.label = None

	def addEdge(self, edge):
		self.edges.append(edge)

	def setLabel(self, label):
		self.label = label

	def __repr__(self):
		return "(" + str(self.x()) + ", " + str(self.y()) + ", " + str(self.z()) + ")"


class MyM3R(QMatrix3x3):

	def __init__(self, data):
		super().__init__(data)

	def transform(self, vector):
		newVector = [0, 0, 0]
		for i in range(3):
			newVector[i] = self[i, 0] * vector.x() + self[i, 1] * vector.y() + self[i, 2] * vector.z()
		vector.setX(newVector[0])
		vector.setY(newVector[1])
		vector.setZ(newVector[2])

	def __repr__(self):
		string = " / "
		for i in range(3):
			for j in range(3):
				string += str(self[i, j])
				if j != 2:
					string += "  "
			if i == 0:
				string += " \\\n｜ "
			elif i == 1:
				string += " ｜\n \\ "
			else:
				string += " /"
		return string


class Vertex3DCircle(QGraphicsEllipseItem):
	def __init__(self, vertex):
		self.radius = 5
		rect = QRectF(vertex.x() - self.radius, vertex.y() - self.radius, self.radius * 2, self.radius * 2)
		super().__init__(rect)
		self.vertex = vertex
		self.pen = QPen(Qt.black)
		self.brush = QBrush(Qt.black, Qt.SolidPattern)
		self.setPen(self.pen)
		self.setBrush(self.brush)

	def contains(self, point):
		center = QVector2D(self.vertex.x() + 12, self.vertex.y())
		vector = QVector2D(point)
		diff = center - vector
		if diff.length() < self.radius + 1:
			return True
		else:
			return False

	def move(self):
		self.radius = 10 * self.vertex.z() / self.scene().height()
		self.setRect(QRectF(self.vertex.x() - self.radius, self.vertex.y() - self.radius, self.radius * 2, self.radius * 2))


class Edge3D(QGraphicsLineItem):
	def __init__(self, vertex1, vertex2):
		self.vertex1 = vertex1
		self.vertex2 = vertex2
		line = QLineF(self.vertex1.toPointF(), self.vertex2.toPointF())
		super().__init__(line)

	def move(self):
		newLine = QLineF(self.vertex1.toPointF(), self.vertex2.toPointF())
		self.setLine(newLine)


class Graph3D(object):

	def __init__(self, *vertices):
		self.vertices = list(vertices)
		self.edges = []

	def addEdge(self, vertex1Index, vertex2Index):
		vertex1 = self.vertices[vertex1Index]
		vertex2 = self.vertices[vertex2Index]
		edge = Edge3D(vertex1, vertex2)
		self.edges.append(edge)
		vertex1.addEdge(edge)
		vertex2.addEdge(edge)

	def numOfVertices(self):
		return len(self.vertices)

	def numOfEdges(self):
		return len(self.edges)

	def repulsiveForces(self, kValue):
		for (i, vertex) in enumerate(self.vertices):
			changeDisp = QVector3D(0, 0, 0)
			for (j, anotherVertex) in enumerate(self.vertices):
				if i != j:
					differenceVector = QVector3D(vertex - anotherVertex)
					if differenceVector.length() < 0.1:
						differenceVector.setX(random.random() - 0.5)
						differenceVector.setY(random.random() - 0.5)
					if abs(differenceVector.z()) < 0.1:
						differenceVector.setZ(random.random() - 0.5)
					changeDisp += differenceVector * pow(kValue, 2) / pow(differenceVector.length(), 2)
			vertex.disp += changeDisp

	def attractiveForces(self, kValue):
		for edge in self.edges:
			differenceVector = QVector3D(edge.vertex1 - edge.vertex2)
			changeDisp = differenceVector * differenceVector.length() / kValue
			edge.vertex1.disp -= changeDisp
			edge.vertex2.disp += changeDisp

	def centering(self, center):
		graphCenter = QVector3D(0, 0, 0)
		for vertex in self.vertices:
			graphCenter += vertex
		graphCenter = graphCenter / self.numOfVertices()
		changeDisp = center - graphCenter
		for vertex in self.vertices:
			vertex.disp += changeDisp

	def displacement(self, kValue, center):
		for vertex in self.vertices:
			vertex.disp = QVector3D(0, 0, 0)
		self.repulsiveForces(kValue)
		self.attractiveForces(kValue)
		self.centering(center)

	def move(self, temperature, area, center):
		edgeVertexRate = self.numOfEdges() / self.numOfVertices()
		kValue = math.sqrt(area / self.numOfVertices() / 40) * edgeVertexRate
		self.displacement(kValue, center)
		for vertex in self.vertices:
			dispLength = vertex.disp.length()
			vertex += (vertex.disp / dispLength) * min(dispLength, temperature)

	def __repr__(self):
		return str(self.vertices)


class MyView(QGraphicsView):

	def __init__(self, scene, parent):
		super().__init__(scene, parent)

	def center(self):
		widget = self.parent()
		return QVector3D(widget.height() / 2, widget.height() / 2, widget.height() / 2)

	def mousePressEvent(self, event):
		for vertex in self.parent().graph.vertices:
			if vertex.circle.contains(event.pos() + self.pos()) and vertex.label != None:
				self.parent().labelLine.setText(vertex.label)
				break
		widget = self.parent()
		if widget.timerID != 0:
			widget.killTimer(widget.timerID)
			widget.timerID = 0
		self.verticesPosWhenClicked = []
		self.mousePosWhenClicked = event.pos()
		for vertex in self.parent().graph.vertices:
			self.verticesPosWhenClicked.append(QVector3D(vertex))

	def mouseMoveEvent(self, event):
		vertices = self.parent().graph.vertices
		verticesPos = [QVector3D(i) for i in self.verticesPosWhenClicked]
		for (pos, afterPos) in zip(self.verticesPosWhenClicked, verticesPos):
			afterPos.setX(pos.x() - self.center().x())
			afterPos.setY(pos.y() - self.center().y())
			afterPos.setZ(pos.z() - self.center().z())
		disp = event.pos() - self.mousePosWhenClicked
		xAngle = QVector2D(disp).length() * 2 * math.pi / 360
		if QVector2D(disp).length() != 0:
			if (-numpy.sign(disp.x())) != 0:
				zAngle = math.acos((-disp.y()) / QVector2D(disp).length()) * (-numpy.sign(disp.x()))
			else:
				zAngle = math.acos((-disp.y()) / QVector2D(disp).length())
		else:
			zAngle = 0
		xTurnList = [1, 0, 0, 0, math.cos(xAngle), -math.sin(xAngle), 0, math.sin(xAngle), math.cos(xAngle)]
		zTurnList = [math.cos(zAngle), -math.sin(zAngle), 0, math.sin(zAngle), math.cos(zAngle), 0, 0, 0, 1]
		minusZTurnList = [math.cos(-zAngle), -math.sin(-zAngle), 0, math.sin(-zAngle), math.cos(-zAngle), 0, 0, 0, 1]
		zTurnMatrix = MyM3R(zTurnList)
		xTurnMatrix = MyM3R(xTurnList)
		minusZTurnMatrix = MyM3R(minusZTurnList)
		for (pos, vertex) in zip(verticesPos, vertices):
			zTurnMatrix.transform(pos)
			xTurnMatrix.transform(pos)
			minusZTurnMatrix.transform(pos)
			vertex.setX(pos.x() + self.center().x())
			vertex.setY(pos.y() + self.center().y())
			vertex.setZ(pos.z() + self.center().z())
		for vertex in vertices:
			vertex.circle.move()
		for edge in self.parent().graph.edges:
			edge.move()

	def mouseReleaseEvent(self, event):
		if self.parent().timerID == 0:
			self.parent().timerID = self.parent().startTimer(1)


class MainWindow3D(QWidget):

	def __init__(self):
		super().__init__()
		self.graph = Graph3D()
		self.initUI()

	def paintEvent(self, event):
		painter = QPainter()
		painter.begin(self)
		option = QStyleOptionGraphicsItem()
		for vertex in self.graph.vertices:
			vertex.circle.paint(painter, option, self.view)
		for edge in self.graph.edges:
			edge.paint(painter, option, self.view)
		painter.end()

	def timerEvent(self, event):
		if self.temperature() > 1:
			self.moveGraph()
			self.autosize()
		else:
			self.killTimer(self.timerID)
			self.timerID = 0

	def moveGraph(self):
		self.graph.move(self.temperature(), self.scene.area, self.view.center())
		for vertex in self.graph.vertices:
			vertex.setX(max(self.height() / 10, min(self.height() / 10 + self.scene.width(), vertex.x())))
			vertex.setY(max(self.height() / 10, min(self.height() / 10 + self.scene.height(), vertex.y())))
			vertex.setZ(max(self.height() / 10, min(self.height() / 10 + self.scene.height(), vertex.z())))
			vertex.circle.move()
		for edge in self.graph.edges:
			edge.move()
		self.scene.stability += 1
		self.update()

	def autosize(self):
		center = self.view.center()
		graphRadius = 0
		for vertex in self.graph.vertices:
			graphRadius = max(graphRadius, (center - vertex).length())
		if graphRadius < self.scene.height() * 11 / 24:
			self.zoomIn()
		else:
			self.zoomOut()

	def stabilization(self):
		if self.timerID != 0:
			self.killTimer(self.timerID)
			self.timerID = 0
		self.timerID = self.startTimer(1)

	def temperature(self):
		return self.scene.height() / self.scene.stability

	def hideEdgeToggle(self, checked):
		if checked:
			for edge in self.graph.edges:
				edge.setVisible(False)
			self.hideEdgeToggleButton.setText("Show edge")
		else:
			for edge in self.graph.edges:
				edge.setVisible(True)
			self.hideEdgeToggleButton.setText("Hide edge")

	def readGraph(self):
		if self.timerID != 0:
			self.killTimer(self.timerID)
			self.timerID = 0
		for vertex in self.graph.vertices:
			self.scene.removeItem(vertex.circle)
		for edge in self.graph.edges:
			self.scene.removeItem(edge)
		readingFile = str(self.selectBox.currentText())
		graphData = __import__("graphData." + readingFile, 
			globals(), locals(), ["vertexCount", "edges", "labels"], 0)
		vertexCount = graphData.vertexCount
		edges = graphData.edges
		labels = graphData.labels
		vertices = []
		for i in range(vertexCount):
			x = self.height() / 2 + self.height() / 5 * math.cos((i / vertexCount) * (2 * math.pi))
			y = self.height() / 2 + self.height() / 5 * math.sin((i / vertexCount) * (2 * math.pi))
			vertices.append(Vertex3D(x, y, 0))
		self.graph = Graph3D(*vertices)
		for (vertex1, vertex2) in edges:
			self.graph.addEdge(vertex1, vertex2)
		for edge in self.graph.edges:
			self.scene.addItem(edge)
		if self.hideEdgeToggleButton.isChecked():
			for edge in self.graph.edges:
				edge.setVisible(False)
		for vertex in self.graph.vertices:
			self.scene.addItem(vertex.circle)
		if labels != None:
			for (vertex, label) in zip(self.graph.vertices, labels):
				vertex.setLabel(label)
		self.scene.stability = 1
		self.update()

	def zoomIn(self):
		self.scene.area *= 1 + self.temperature() / self.scene.height()

	def zoomOut(self):
		self.scene.area *= 1 - self.temperature() / self.scene.height()

	def initUI(self):
		self.exitButton = QPushButton("Exit", self)
		self.exitButton.setShortcut("Ctrl+Q")
		self.exitButton.clicked.connect(qApp.quit)

		self.stabilizationButton = QPushButton("Stabilization", self)
		self.stabilizationButton.clicked.connect(self.stabilization)

		self.hideEdgeToggleButton = QPushButton("Hide edge", self)
		self.hideEdgeToggleButton.toggled.connect(self.hideEdgeToggle)
		self.hideEdgeToggleButton.setCheckable(True)

		self.selectBox = QComboBox(self)
		fileList = [os.path.basename(fileName) for fileName in glob.glob("./graphData/*.py")]
		fileList.remove("__init__.py")
		for index, file in enumerate(fileList):
			self.selectBox.insertItem(index, file[:-3])
		self.selectBox.activated.connect(self.readGraph)

		self.labelLabel = QLabel("Label:", self)
		self.labelLabel.setMaximumSize(120, 20)
		self.labelLine = QLineEdit(self)
		self.labelLine.setReadOnly(True)
		self.labelLine.setMaximumWidth(120)
		self.labelLayout = QVBoxLayout()
		self.labelLayout.addWidget(self.labelLabel)
		self.labelLayout.addWidget(self.labelLine)

		self.toolLayout = QVBoxLayout()
		self.toolLayout.addWidget(self.exitButton)
		self.toolLayout.addWidget(self.stabilizationButton)
		self.toolLayout.addWidget(self.hideEdgeToggleButton)
		self.toolLayout.addLayout(self.labelLayout)
		self.toolLayout.addWidget(self.selectBox)
		
		desktop = QDesktopWidget()
		width = desktop.width() / 2
		height = desktop.height() / 5 * 3
		windowX = desktop.width() / 3
		windowY = desktop.height() / 5
		self.setGeometry(windowX, windowY, width, height)
		sceneRect = QRectF(self.height() / 10, self.height() / 10, self.height() / 10 * 8, self.height() / 10 * 8)
		self.scene = QGraphicsScene(sceneRect, self)
		self.view = MyView(self.scene, self)
		self.scene.area = self.scene.width() * self.scene.height()
		self.scene.stability = 1
		self.setWindowTitle("visibleGraph3D")

		self.mainLayout = QHBoxLayout(self)
		self.mainLayout.addWidget(self.view)
		self.mainLayout.addLayout(self.toolLayout)
		self.setLayout(self.mainLayout)

		self.timerID = 0
		self.readGraph()
		self.show()

if __name__ == '__main__':
	app = QApplication(sys.argv)
	mainWindow = MainWindow3D()
	sys.exit(app.exec_())

