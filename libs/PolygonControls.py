import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from libs.Constants import *
from libs.Utils import *
import math

class Control:
    instances = []

    @staticmethod
    def deleteAllControls():
        Control.instances = []

    def __init__(self, **kwargs):

        self.radius = CONTROL_RADIUS
        self._radius = self.radius
        self.color = QColor(CONTROL_DEFAULT_COLOR)
        self.highlightColor = QColor(CONTROL_HIGHLIGHT_COLOR)
        self.x = 0
        self.y = 0
        self.parent = None
        
        self.__dict__.update(kwargs)

        self.position = QPoint(self.x, self.y)
        self.scaledPosition = QPoint(self.x, self.y)

        Control.instances.append(self)

    def checkClicked(self, position):
        return pointCircleCollision(position, self.position, self.radius)

    def move(self, position):
        self.position = position
        self.parent.updateParameters()

class Polygon:
    def __init__(self, *args, **kwargs):
        self.numControls = NUM_CONTROLS
        self.center = QPoint(POLYGON_START, POLYGON_START)
        self.color = QColor(CONTROL_DEFAULT_COLOR)
        self.highlightColor = QColor(CONTROL_HIGHLIGHT_COLOR)
        self.selectedColor = QColor(CONTROL_SELECTED_COLOR)

        self.__dict__.update(kwargs)

        self.controls = []
        self.boundingBox = QRect()

    def computeBoundingBox(self):
        minX = math.inf
        maxX = -math.inf
        minY = math.inf
        maxY = -math.inf

        for control in self.controls:
            pos = control.position

            if (pos.x() < minX):
                minX = pos.x()

            if(pos.x() > maxX):
                maxX = pos.x()

            if (pos.y() < minY):
                minY = pos.y()

            if(pos.y() > maxY):
                maxY = pos.y()

        width = maxX - minX
        height = maxY - minY

        self.boundingBox = QRect(minX, minY, width, height)

    def checkedPointInBoundingBox(self, position):
        x = self.boundingBox.x()
        y = self.boundingBox.y()
        w = self.boundingBox.width()
        h = self.boundingBox.height()

        return pointRectangleCollision(position, x, y, w, h)

    def move(self, position):
        self.center = position
        
        self.updateOffsets()
        self.updateParameters()

    def updateOffsets(self):
        for i, control in enumerate(self.controls):
            xPos = self.center.x() + self.offsets[i][0]
            yPos = self.center.y() + self.offsets[i][1]

            control.position.setX(xPos)
            control.position.setY(yPos)

    def updateParameters(self):
        self.computeCenter()
        self.computeOffsets()
        self.computeBoundingBox()

    def computeCenter(self):
        controlPositions = []
        for control in self.controls:
            controlPositions.append(control.position)

        x, y = averagePosition(controlPositions)
        self.center = QPoint(x, y)
            
    def computeOffsets(self):
        self.offsets = []
        centerX = self.center.x()
        centerY = self.center.y()

        for control in self.controls:
            cPosX = control.position.x()
            cPosY = control.position.y()

            offsetX = cPosX - centerX 
            offsetY = cPosY - centerY

            self.offsets.append([offsetX, offsetY])
    
    def addControl(self):
        control = Control(x=self.center.x(), 
            y=self.center.y(), 
            color=self.color, 
            parent=self)

        self.controls.append(control)
        self.updateParameters()

    def addControlAtPosition(self, position):
        control = Control(x=position.x(), 
                            y=position.y(),
                            color = self.color,
                            parent=self)

        self.controls.append(control)

    def addControlAtIndex(self, index, position):
        control = Control(x=position.x(), 
                            y=position.y(),
                            color = self.color,
                            parent=self)

        self.controls.insert(index, control)

    def deleteLastControl(self):
        self.controls.pop()

    def toQPointList(self):
        positions = QPolygonF()

        for control in self.controls:
            positions.append(control.position)

        return positions

    def toList(self):
        positions = []

        for control in self.controls:
            positions.append([control.position.x(), control.position.y()])

        return positions

    def loadPolygonFromList(self, polygons):
        for polygon in polygons:
            pass

    def colorToCV(self):
        color = self.color.getRgb()
        color = (color[0], color[1], color[2])
        return color

    def setFromListOfCotnrolPositions(self, controlsList):
        self.controls = []
        
        for pos in controlsList:
            control = Control(x=pos[0], y=pos[1],
                                color=self.color,
                                parent=self)

            self.controls.append(control)

    def deleteControl(self, control):
        index = self.controls.index(control)
        self.controls.pop(index)

    def copyControls(self, controls, offset=0):
        self.controls = []
        for control in controls:
            newControl = Control(x=control.position.x() + offset, 
                                y=control.position.y() + offset,
                                color=self.color,
                                parent=self)
            self.controls.append(newControl)

    def setColor(self, color):
        newColor = color

        if(type(newColor) is str):
            newColor = QColor(newColor)

        self.color = color
        for control in self.controls:
            control.color = color
