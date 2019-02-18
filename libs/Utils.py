import math
from libs.Constants import *

def scale(value, minOld, maxOld, minNew, maxNew):
    oldRange = maxOld - minOld
    newRange = maxNew - minNew

    return (((value - minOld) * newRange) / oldRange) + minNew

def clamp(value, minVal, maxVal):

    newValue = value

    if(value > maxVal):
        newValue = maxVal
    elif(value< minVal):
        newValue = minVal

    return newValue

def pointRectangleCollision(mousePos, x, y, w, h):
	mouseX = mousePos.x()
	mouseY = mousePos.y()

	if(mouseX > x and mouseX < x + w):
		if(mouseY > y and mouseY < y + h):
			return True
	else:
		return False

def pointCircleCollision(mousePos, controlPos, radius):
	mouseX = mousePos.x()
	mouseY = mousePos.y()
	xDiff = (mouseX - controlPos.x()) ** 2
	yDiff = (mouseY - controlPos.y()) ** 2

	if(math.sqrt(xDiff + yDiff) < radius):
	    return True
	else:
	    return False

#Used for polygon hit detection
def getWhichSideOfLine(point, lineStart, lineEnd):
	x = point[0]
	y = point[1]
	
	x1 = lineStart[0]
	y1 = lineStart[1]
	
	x2 = lineEnd[0]
	y2 = lineEnd[1]
	
	d = ((x - x1) * (y2 - y1)) - ((y - y1) * (x2-x1))
	
	return d * -1

def distance(pos1, pos2):
	x1, y1 = pos1
	x2, y2 = pos2

	xDiff = (x1 - x2) ** 2
	yDiff = (y1 - y2) ** 2

	return xDiff + yDiff

def getClosestLine(pos, polygon):

	minDistance = math.inf
	closestLineIndexes = []
	intersectionPos = None

	vLine = [pos.x(), pos.y() + MOUSE_SEARCH_AREA, pos.x(), pos.y() - MOUSE_SEARCH_AREA] 
	hLine = [pos.x() - MOUSE_SEARCH_AREA, pos.y(), pos.x() + MOUSE_SEARCH_AREA, pos.y()]

	for i in range(len(polygon.controls)):
		startIndex = i
		endIndex = 0

		if(i < len(polygon.controls) - 1):
			endIndex = i + 1
		else:
			endIndex = 0

		lineStart = polygon.controls[startIndex]
		lineEnd = polygon.controls[endIndex]

		lineStart = [lineStart.position.x(), lineStart.position.y()]
		lineEnd = [lineEnd.position.x(), lineEnd.position.y()]
		line = [lineStart[0], lineStart[1], lineEnd[0], lineEnd[1]]

		point = [pos.x(), pos.y()]

		intersectionV = linesIntersect(vLine, line)
		intersectionH = linesIntersect(hLine, line)

		intersection = None

		if(intersectionV is None):
			intersection = intersectionH
		else:
			intersection = intersectionV

		distanceToLine = math.inf
		if(intersection is not None):
			distanceToLine = distance([pos.x(), pos.y()], [intersection['x'], intersection['y']])

		if(distanceToLine < minDistance):
			minDistance = distanceToLine
			closestLineIndexes = [startIndex, endIndex]

	if(intersectionPos is not None):
		intersectionPos = [intersectionPos['x'], intersectionPos['y']]	

	return minDistance, closestLineIndexes

def averagePosition(positions):
	sumX = 0
	sumY = 0

	for pos in positions:
		sumX += pos.x()
		sumY += pos.y()

	sumX /= len(positions)
	sumY /= len(positions)

	return sumX, sumY


def pointInsidePolygon(pos, polygon):
	numOverlappingLines = 0

	# +0.00001 stops fasle detections when mouse is at the EXACT same y position as controls
	mouseLine = [pos.x(), pos.y() + 0.00001, pos.x() + 10000, pos.y() + + 0.00001]

	for i, pos in enumerate(polygon):
		if(i < len(polygon) - 1):
			nextPos = polygon[i+1]
		else:
			nextPos = polygon[0]

		polyLine = [pos[0], pos[1], nextPos[0], nextPos[1]]

		if(linesIntersect(mouseLine, polyLine) is not None):
			numOverlappingLines += 1

	if(numOverlappingLines % 2 == 0):
		return False
	else:
		return True


def linesIntersect(line1, line2):
	'''
	From https://www.youtube.com/watch?v=A86COO8KC58&ab_channel=CodingMath
	lineX = [startX, startY, endX, endY]
	'''
	p0 = {'x': line1[0], 'y': line1[1]}
	p1 = {'x': line1[2], 'y': line1[3]}
	p2 = {'x': line2[0], 'y': line2[1]}
	p3 = {'x': line2[2], 'y': line2[3]}
	
	a1 = p1['y'] - p0['y']
	b1 = p0['x']  - p1['x'] 
	c1 = a1 * p0['x']  + b1 * p0['y'] 
	a2 = p3['y'] - p2['y'] 
	b2 = p2['x'] - p3['x'] 
	c2 = a2 * p2['x']  + b2 * p2['y'] 
	
	denominator = a1 * b2 - a2 * b1
	
	if(denominator == 0):
		return None
	
	intersect = {'x': (b2 * c1 - b1 * c2) / denominator,
				 'y': (a1 * c2 - a2 * c1) / denominator}

	rx0 = math.inf
	ry0 = math.inf
	rx1 = math.inf
	ry1 = math.inf

	try:
		rx0 = (intersect['x'] - p0['x']) / (p1['x'] - p0['x'])
	except ZeroDivisionError:
		pass

	try:
		ry0 = (intersect['y'] - p0['y']) / (p1['y'] - p0['y'])
	except ZeroDivisionError:
		pass

	try:
		rx1 = (intersect['x'] - p2['x']) / (p3['x'] - p2['x'])
	except ZeroDivisionError:
		pass

	try:
		ry1 = (intersect['y'] - p2['y']) / (p3['y'] - p2['y'])
	except ZeroDivisionError:
		pass

	if(((rx0 >= 0 and rx0 <= 1) or (ry0 >= 0 and ry0 <= 1)) and ((rx1 >= 0 and rx1 <= 1) or (ry1 >= 0 and ry1 <= 1))):
		return intersect
	else:
		return None

