#!/usr/bin/env python
# coding: utf-8

import sys

def hasOverlapping(*lst):
	uniqueList = []
	for content in lst:
		if content in uniqueList:
			return True
		else:
			uniqueList.append(content)
	return False

if __name__ == "__main__":
	fileName = input("type fileName removed \".py\" --> ")
	while True:
		allowToClear = input("Is it OK to clear this file?  y / n : ").strip()
		if allowToClear.lower() == "y":
			with open("./graphData/" + fileName + ".py", "w", encoding="utf-8") as file:
				file.write("")
				file.close()
			break
		elif allowToClear.lower() == "n":
			print("exit")
			sys.exit(0)
	writeStrings = []
	writeStrings.append("# coding: utf-8\n")
	writeStrings.append("\n")
	while True:
		vertexCount = input("type vertexCount --> ").strip()
		if not vertexCount.isdecimal():
			print("must type a number")
			continue
		if int(vertexCount) <= 0:
			print("must type a positive number")
			continue
		if int(vertexCount) > 100:
			print("must type a number of 100 or less")
			continue
		break
	writeStrings.append("vertexCount = " + vertexCount + "\n")
	writeStrings.append("\n")
	writeStrings.append("edges = [\n")
	verticesList = range(int(vertexCount))
	for i in verticesList:
		while True:
			print("type vertexNumbers which connect vertex " + str(i) + " with split \",\"")
			verticesData = input("--> ")
			verticesData = verticesData.rstrip(", ")
			connectVertices = list(map(lambda s: s.strip(), verticesData.split(",")))
			writeString = "\t"
			error = False
			if connectVertices == [""]:
				if i == int(vertexCount) - 1:
					writeStrings[-1] = writeStrings[-1].rstrip(", \n")
				break
			if hasOverlapping(*connectVertices):
				print("each vertex must be unique")
				continue
			for vertex in connectVertices:
				if not vertex.isdecimal():
					print("each vertex expression must be a number")
					error = True
					break
				if int(vertex) >= int(vertexCount):
					print("It contains unknown vertices")
					error = True
					break
				if int(vertex) <= i:
					print("each vertex number must be more than " + str(i))
					error = True
					break
				writeString += ("(" + str(i) + ", " + str(vertex) + "), ")
			if error:
				continue
			writeStrings.append(writeString + "\n")
			break
	with open("./graphData/" + fileName + ".py", "a", encoding="utf-8") as file:
		file.writelines(writeStrings)
		file.write("\n")
		file.write("]\n")
		file.write("\n")
		file.write("labels = None\n")
		file.write("\n")
		file.close()


