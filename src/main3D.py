#!/usr/bin/env python
# coding: utf-8

from PyQt5.QtWidgets import QGraphicsEllipseItem, QGraphicsLineItem, QStyleOptionGraphicsItem
from PyQt5.QtCore import QRectF, Qt, QLineF
from PyQt5.QtGui import QVector3D, QPen, QBrush, QVector2D, QPainter

class Vertex3D(QVector3D):
	def __init__(self, x, y, z):
		super().__init__(x, y, z)
		self.disp = QVector3D(0, 0, 0)
		self.edges = []
		self.circle = VertexCircle(self)

	def addEdge(self, edge):
		self.edges.append(edge)

	def __repr__(self):
		return "(" + str(self.x()) + ", " + str(self.y()) + ", " + str(self.z()) + ")"

class VertexCircle(QGraphicsEllipseItem):
	def __init__(self, vertex):
		self.RADIUS = 5
		rect = QRectF(vertex.x() - self.RADIUS, vertex.y() - self.RADIUS, self.RADIUS * 2, self.RADIUS * 2)
		super().__init__(rect)
		self.vertex = vertex
		self.pen = QPen(Qt.black)
		self.brush = QBrush(Qt.black, Qt.SolidPattern)
		self.setPen(self.pen)
		self.setBrush(self.brush)

	def move(self):
		self.setRect(QRectF(self.vertex.x() - self.RADIUS, self.vertex.y() - self.RADIUS, self.RADIUS * 2, self.RADIUS * 2))

class Edge(QGraphicsLineItem):
	def __init__(self, vertex1, vertex2):
		self.vertex1 = vertex1
		self.vertex2 = vertex2
		line = QLineF(self.vertex1.toPointF(), self.vertex2.toPointF())
		super().__init__(line)

	def move(self):
		newLine = QLineF(self.vertex1.toPointF(), self.vertex2.toPointF())
		self.setLine(newLine)

class Graph(object):
	def __init__(self, *vertices):
		self.vertices = list(vertices)
		self.edges = []

	def addEdge(self, vertex1Index, vertex2Index):
		vertex1 = self.vertices[vertex1Index]
		vertex2 = self.vertices[vertex2Index]
		edge = Edge(vertex1, vertex2)
		self.edges.append(edge)
		vertex1.addEdge(edge)
		vertex2.addEdge(edge)

	def numOfVertices(self):
		return len(self.vertices)

	def numOfEdges(self):
		return len(self.edges)

	def repulsiveForces(self, kValue):
		for (i, vertex) in enumerate(self.vertices):
			changeDisp = QVector2D(0, 0)
			for (j, anotherVertex) in enumerate(self.vertices):
				if i != j:
					differenceVector = QVector2D(vertex - anotherVertex)
					if differenceVector.length() < 0.1:
						differenceVector.setX(random.random() - 0.5)
						differenceVector.setY(random.random() - 0.5)
					changeDisp += differenceVector * pow(kValue, 2) / pow(differenceVector.length(), 2)
			vertex.disp += changeDisp

	def attractiveForces(self, kValue):
		for edge in self.edges:
			differenceVector = QVector2D(edge.vertex1 - edge.vertex2)
			changeDisp = differenceVector * differenceVector.length() / kValue
			edge.vertex1.disp -= changeDisp
			edge.vertex2.disp += changeDisp

	def displacement(self, kValue):
		for vertex in self.vertices:
			vertex.disp = QVector2D(0, 0)
		self.repulsiveForces(kValue)
		self.attractiveForces(kValue)

	def move(self, temperature, area):
		edgeVertexRate = self.numOfEdges() / self.numOfVertices()
		kValue = math.sqrt(area / self.numOfVertices() / 40) * edgeVertexRate
		self.displacement(kValue)
		for vertex in self.vertices:
			dispLength = vertex.disp.length()
			vertex += (vertex.disp / dispLength) * min(dispLength, temperature)

	def __repr__(self):
		return str(self.vertices)

class MainWindow(QWidget):

	def __init__(self):
		super().__init__()
		self.graph = Graph()
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
		else:
			self.killTimer(self.timerID)
			self.timerID = 0

	def moveGraph(self):
		self.graph.move(self.temperature(), self.scene.area)
		for vertex in self.graph.vertices:
			vertex.setX(max(self.height() / 10, min(self.height() / 10 + self.scene.width(), vertex.x())))
			vertex.setY(max(self.height() / 10, min(self.height() / 10 + self.scene.height(), vertex.y())))
			vertex.circle.move()
			vertex.fixSign.move()
		for edge in self.graph.edges:
			edge.move()
		self.scene.stability += 1
		self.update()

	def stabilization(self):
		if self.timerID != 0:
			self.killTimer(self.timerID)
			self.timerID = 0
		self.timerID = self.startTimer(1)

	def temperature(self):
		return self.scene.height() / self.scene.stability

	def colorToggle(self, checked):
		if self.timerID != 0:
			self.killTimer(self.timerID)
			self.timerID = 0
		if checked:
			self.graph.colored = True
			self.colorToggleButton.setText("Uncolor")
		else:
			self.graph.colored = False
			self.colorToggleButton.setText("Color")
		self.scene.stability = 1
		self.stabilization()

	def visibleEdgeToggle(self, checked):
		if checked:
			for edge in self.graph.edges:
				edge.setVisible(False)
			self.visibleEdgeToggleButton.setText("Visible edge")
		else:
			for edge in self.graph.edges:
				edge.setVisible(True)
			self.visibleEdgeToggleButton.setText("Invisible edge")

	def readGraph(self):
		if self.timerID != 0:
			self.killTimer(self.timerID)
			self.timerID = 0
		self.graph.colored = False
		self.colorToggleButton.setChecked(False)
		self.colorToggleButton.setText("Color")
		for vertex in self.graph.vertices:
			self.scene.removeItem(vertex.circle)
		for edge in self.graph.edges:
			self.scene.removeItem(edge)
		readingFile = str(self.selectBox.currentText())
		graphData = __import__("graphData." + readingFile, 
			globals(), locals(), ["vertexCount", "edges"], 0)
		vertexCount = graphData.vertexCount
		edges = graphData.edges
		vertices = []
		for i in range(vertexCount):
			x = self.height() / 2 + self.height() / 5 * math.cos((i / vertexCount) * (2 * math.pi))
			y = self.height() / 2 + self.height() / 5 * math.sin((i / vertexCount) * (2 * math.pi))
			vertices.append(Vertex(x, y))
		self.graph = Graph(*vertices)
		for (vertex1, vertex2) in edges:
			self.graph.addEdge(vertex1, vertex2)
		for edge in self.graph.edges:
			self.scene.addItem(edge)
		if self.visibleEdgeToggleButton.isChecked():
			for edge in self.graph.edges:
				edge.setVisible(False)
		for vertex in self.graph.vertices:
			self.scene.addItem(vertex.circle)
		self.scene.stability = 1
		self.update()

	def releaseFixedVertices(self):
		if self.timerID != 0:
			self.killTimer(self.timerID)
			self.timerID = 0
		for vertex in self.graph.vertices:
			vertex.release()
		self.scene.stability = min(16, self.scene.stability)
		self.stabilization()

	def initUI(self):
		self.exitButton = QPushButton("Exit", self)
		self.exitButton.setShortcut("Ctrl+Q")
		self.exitButton.clicked.connect(qApp.quit)

		self.stabilizationButton = QPushButton("Stabilization", self)
		self.stabilizationButton.clicked.connect(self.stabilization)

		self.releaseButton = QPushButton("Release", self)
		self.releaseButton.clicked.connect(self.releaseFixedVertices)

		self.colorToggleButton = QPushButton("Color", self)
		self.colorToggleButton.clicked.connect(self.colorToggle)
		self.colorToggleButton.setCheckable(True)

		self.visibleEdgeToggleButton = QPushButton("Invisible edge", self)
		self.visibleEdgeToggleButton.toggled.connect(self.visibleEdgeToggle)
		self.visibleEdgeToggleButton.setCheckable(True)

		self.selectBox = QComboBox(self)
		fileList = [os.path.basename(fileName) for fileName in glob.glob("./graphData/*.py")]
		fileList.remove("__init__.py")
		for index, file in enumerate(fileList):
			self.selectBox.insertItem(index, file[:-3])
		self.selectBox.activated.connect(self.readGraph)

		self.toolLayout = QVBoxLayout()
		self.toolLayout.addWidget(self.exitButton)
		self.toolLayout.addWidget(self.stabilizationButton)
		self.toolLayout.addWidget(self.releaseButton)
		self.toolLayout.addWidget(self.colorToggleButton)
		self.toolLayout.addWidget(self.visibleEdgeToggleButton)
		self.toolLayout.addWidget(self.selectBox)
		
		desktop = QDesktopWidget()
		width = desktop.width() / 2
		height = desktop.height() / 5 * 3
		windowX = desktop.width() / 3
		windowY = desktop.height() / 5
		self.setGeometry(windowX, windowY, width, height)
		sceneRect = QRectF(self.height() / 10, self.height() / 10, self.height() / 10 * 8, self.height() / 10 * 8)
		self.scene = QGraphicsScene(sceneRect, self)
		self.view = QGraphicsView(self.scene, self)
		self.scene.area = self.scene.width() * self.scene.height()
		self.scene.stability = 1
		self.setWindowTitle("visibleGraph")

		self.mainLayout = QHBoxLayout(self)
		self.mainLayout.addWidget(self.view)
		self.mainLayout.addLayout(self.toolLayout)
		self.setLayout(self.mainLayout)

		self.timerID = 0

		self.readGraph()
		self.show()

if __name__ == '__main__':
	app = QApplication(sys.argv)
	mainWindow = MainWindow()
	sys.exit(app.exec_())

