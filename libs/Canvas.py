from PyQt5.QtWidgets import QMessageBox, QColorDialog, QWidget,  QMenu
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QColor, QStandardItem
from PyQt5.QtCore import QPoint, QPointF, Qt
from libs.PolygonControls import Control, Polygon
from libs.Constants import *
from libs.Utils import *
import numpy as np
import cv2, math, sys, pickle, os

class Canvas(QWidget):
    
    def __init__(self, **kwargs):
        super(Canvas, self).__init__(**kwargs)

        self.pixmap = QPixmap()
        self.filenamePrefix = ""

        self.scale = DEFAULT_SCALE
        self.scaleMax = MAX_SCALE
        self.scaleMin = MIN_SCALE
        self.scaleIncrement = ZOOM_INCREMENT

        self.painter = QPainter()
        self.setMouseTracking(True)
        self.color = QColor(CANVAS_DEFAULT_COLOR)

        self.parentCenterX = 0
        self.parentCenterY = 0
        self.canvasCenterX = self.pixmap.width() // 2
        self.canvasCenterY = self.pixmap.height() // 2

        self.canvasWidth = int(self.pixmap.width() * self.scale)
        self.canvasHeight = int(self.pixmap.height() * self.scale)

        self.canvasGlobalLeft = 0
        self.canvasGlobalRight = 0
        self.canvasGlobalTop = 0
        self.canvasGlobalBottom = 0

        self.controlOpacity = CONTROL_OPACITY
        self.polygons = []

        self.mouseHeld = False
        self.middleClickHeld = False
        self.mouseDownPos = QPoint()
        self.mousePos = QPoint()
        self.previousMousePos = QPoint()

        self.highlightedControl = None
        self.clickedControl = None
        self.selectedPolygon = None
        self.freeDrawPolygon = None
        self.closestLine = None
        self.controlOffset = QPoint()
        self.copyOfSelectedPolygon = None
        self.hideControls = False

        self.vBarPos = 0
        self.hBarPos = 0
        self.hBar = None
        self.vBar = None

        self.state = MOVE_CONTROLS

        self.update()
        self.updateCanvasGlobalParameters()

    def showEvent(self, event):
        '''
        Used for making sure the correct width/height of the screen is used

        Inside __init__(), parent.size = (1280, 720) 
            (doesn't take into account margins, 
            incorrect mouse positions)

        When running, parent.size = (1278, 667)
            (Does take into account margins, 
            correct mouse positions)
        '''

        parent = self.parent().window()

        self.hBar = parent.scrollArea.horizontalScrollBar()
        self.vBar = parent.scrollArea.verticalScrollBar()
        self.updateCanvasGlobalParameters()

    def paintEvent(self, event):
        if(not self.pixmap.isNull()):
            self.painter.begin(self)

            self.setPainterQuality()

            self.painter.scale(self.scale, self.scale)
            self.painter.translate(self.offsetToCenter())

            self.drawImage()
            self.drawPolygons()

            if(self.closestLine is not None and self.selectedPolygon is not None and type(self.highlightedControl) is not Control):
                self.drawClosestLineControls()

            if(self.state == DRAW_POLYGON):
                self.drawMouseTargets()

            self.painter.end()

    def sizeHint(self):
        return self.minimumSizeHint()

    def minimumSizeHint(self):
        if self.pixmap:
            return self.scale * self.pixmap.size()
        return super(Canvas, self).minimumSizeHint()

    def drawImage(self):
        self.painter.setOpacity(1)
        self.painter.drawPixmap(0, 0, self.pixmap)

    def drawPolygons(self):
        for poly in self.polygons:
            self.painter.setOpacity(CONTROL_OPACITY)
            
            if(not self.hideControls):
                self.drawControls(poly.controls)
            elif(poly == self.selectedPolygon):
                self.drawControls(poly.controls)
            elif(poly == self.freeDrawPolygon):
                self.drawControls(poly.controls)

            self.painter.setBrush(poly.color)

            if(poly == self.selectedPolygon and poly == self.highlightedControl):
                self.painter.setOpacity(HIGHLIGHTED_OPACITY)
                self.painter.setPen(QColor(CONTROL_HIGHLIGHT_COLOR))
            elif(poly == self.selectedPolygon):
                self.painter.setPen(QColor(CONTROL_HIGHLIGHT_COLOR))
                self.painter.setOpacity(SELECTED_OPACITY)

            elif(poly == self.highlightedControl):
                self.painter.setOpacity(HIGHLIGHTED_OPACITY)

            else:
                self.painter.setPen(Qt.NoPen)
                

            self.painter.drawPolygon(poly.toQPointList())

    def drawControls(self, controls):
        for control in controls:
            self.painter.setBrush(control.color)

            if(control == self.highlightedControl):
                self.painter.setOpacity(HIGHLIGHTED_OPACITY)
            else:
                self.painter.setPen(Qt.NoPen)
                self.painter.setOpacity(CONTROL_OPACITY)

            self.painter.drawEllipse(control.position,
                                    control.radius,
                                    control.radius)
    def drawClosestLineControls(self):
        scaledPos = self.scaleMousePos()
        self.painter.setPen(QColor(CLOSEST_LINE_COLOR))
        line = self.closestLine
        start = self.selectedPolygon.controls[line[0]].position
        end = self.selectedPolygon.controls[line[1]].position

        self.painter.drawLine(start.x(), start.y(), end.x(), end.y())

        self.painter.setBrush(self.selectedPolygon.color)
        self.painter.drawEllipse(self.getClosestLineIntersection(), 
                                CONTROL_RADIUS / self.scale, 
                                CONTROL_RADIUS / self.scale)

    def drawMouseTargets(self):
        scaledPos = self.scaleMousePos()
        self.painter.setPen(Qt.black)
        self.painter.pen().setWidth(MOUSE_TARGET_THICKNESS)
        self.painter.drawLine(0, scaledPos.y(), self.pixmap.width(), scaledPos.y())
        self.painter.drawLine(scaledPos.x(), 0, scaledPos.x(), self.pixmap.height())

    def mousePressEvent(self, event):
        if(not self.pixmap.isNull()):
            self.mouseHeld = True
            self.mouseDownPos = self.scaleMousePos()
            self.previousMousePos = self.mouseDownPos

            if(event.button() == Qt.LeftButton):
                self.handleLeftClick(event)
            elif(event.button() == Qt.MiddleButton):
                self.handleMiddleClick(event)
            elif(event.button() == Qt.RightButton):
                self.handleRightClick(event)

    def mouseMoveEvent(self, event):
        if(not self.pixmap.isNull()):
            self.mousePos = event.pos()
            scaledPos = self.scaleMousePos()
            self.closestLine = None

            if(self.middleClickHeld):
                self.scrollWindow(scaledPos)
            else:
                self.moveControls(scaledPos)

            self.parent().window().labelCoordinates.setText(
                    f"X: {scaledPos.x()}; Y: {scaledPos.y()}")

            self.update()

    def scrollWindow(self, scaledPos):
        move = (scaledPos - self.previousMousePos) * SCROLL_SCALE
        self.hBar.setValue(self.hBar.value() - move.x())
        self.vBar.setValue(self.vBar.value() - move.y())

        self.previousMousePos = scaledPos

    def moveControls(self, scaledPos):
        if(self.clickedControl is not None):
            newPos = scaledPos
            validPos = True

            if(type(self.clickedControl) is Polygon):
                prevPos = self.clickedControl.center
                newPos += self.controlOffset
                self.clickedControl.move(newPos)

                for control in self.clickedControl.controls:
                    if(control.position.x() < 0):
                        validPos = False
                        newPos.setX(prevPos.x())
                    elif(control.position.x() > self.pixmap.width()):
                        validPos = False
                        newPos.setX(prevPos.x())

                    if(control.position.y() < 0):
                        validPos = False
                        newPos.setY(prevPos.y())
                    elif(control.position.y() >= self.pixmap.height()):
                        validPos = False
                        newPos.setY(prevPos.y())

                if(not validPos):
                    self.clickedControl.move(newPos)
            else:
                self.clickedControl.move(newPos)

            self.parent().window().saved = False

        elif(self.state is not DRAW_POLYGON):
            self.highlightedControl = self.checkIfHoveringOverControl(scaledPos)


        if(self.selectedPolygon is not None and type(self.selectedPolygon)) is Polygon and type(self.highlightedControl) is not Control:
            distance, indexes = getClosestLine(self.scaleMousePos(), self.selectedPolygon)
            if(distance < CONTROL_MIN_LINE_DISTANCE):
                self.closestLine = indexes

                self.state = ADD_CONTROL
            elif(self.state is not DRAW_POLYGON):
                self.state = MOVE_CONTROLS
        else:
            self.closestLine = None
            if(self.state is not DRAW_POLYGON):
                self.state = MOVE_CONTROLS

    def mouseReleaseEvent(self, event):
        self.clickedControl = None
        self.mouseHeld = False
        self.middleClickHeld = False

    def wheelEvent(self, event):
        if(event.angleDelta().y() >= 0):
            self.scale += self.scaleIncrement
        else:
            self.scale -= self.scaleIncrement

        self.scale = clamp(self.scale, self.scaleMin, self.scaleMax)

        self.hBar.setValue(self.hBar.value())
        self.vBar.setValue(self.vBar.value())

        self.updateControlRadius()
        self.updateCanvasGlobalParameters()

        self.update()
        self.adjustSize()

    def handleLeftClick(self, event):
        self.mouseDownPos = event.pos()
        scaledPos = self.scaleMousePos()

        if(self.state == MOVE_CONTROLS):
            if(self.highlightedControl is not None):
                self.clickedControl = self.highlightedControl
                if(type(self.clickedControl) is Polygon):
                    self.controlOffset = self.clickedControl.center - scaledPos
            self.updateSelectedPolygon()
        elif(self.state == ADD_CONTROL):
            index = self.closestLine[1]
            self.selectedPolygon.addControlAtIndex(index, scaledPos)
            self.selectedPolygon.updateParameters()
            self.updateControlRadius()
            self.state = MOVE_CONTROLS
        elif(self.state == DRAW_POLYGON):
            if(self.freeDrawPolygon is None):
                poly = Polygon(color=self.color)
                poly.controls = []
                poly.addControlAtPosition(self.scaleMousePos())
                poly.computeBoundingBox()
                self.polygons.append(poly)
                self.freeDrawPolygon = poly

                self.updateControlRadius()
                self.update()
            else:
                self.freeDrawPolygon.addControlAtPosition(self.scaleMousePos())
                self.freeDrawPolygon.updateParameters()
                self.updateControlRadius()

        self.update()

    def handleMiddleClick(self, event):
        self.middleClickHeld = True

    def deleteControl(self):
        control = self.highlightedControl
        control.parent.deleteControl(control)
        control.parent.updateParameters()

    def handleRightClick(self, event):
        pos = event.pos()
        scaledPos = self.scaleMousePos()

        menu = QMenu(self)
        menu.setStyleSheet(STYLE_SHEET)
        changeColorAciton = menu.addAction("Change Color")

        menu.addSeparator()
        copyAction = menu.addAction(COPY_TEXT)
        pasteAction = menu.addAction(PASTE_TEXT)

        menu.addSeparator()
        deleteControlAction = menu.addAction(DELETE_CONTROL_TEXT)
        deletePolygonAction = menu.addAction(DELETE_POLYGON_TEXT)

        if(self.highlightedControl is None):
            changeColorAciton.setDisabled(True)
            copyAction.setDisabled(True)
            deletePolygonAction.setDisabled(True)
            deleteControlAction.setDisabled(True)
        elif(self.selectedPolygon is None):
            changeColorAciton.setDisabled(True)
        elif(type(self.highlightedControl) is Polygon):
            deleteControlAction.setDisabled(True)
        elif(type(self.highlightedControl) is Control):
            deletePolygonAction.setDisabled(True)
            copyAction.setDisabled(True)

        selectedAction = menu.exec_(self.mapToGlobal(event.pos()))

        if(selectedAction == changeColorAciton):
            self.askForColorChange()
        elif(selectedAction == copyAction):
            self.copyPolygon()
        elif(selectedAction == pasteAction):
            self.pastePolygon()
        elif(selectedAction == deleteControlAction):
            self.deleteControl()
        elif(selectedAction == deletePolygonAction):
            self.deletePolygon()

        self.update()

    def updateSelectedPolygon(self):
        if(type(self.clickedControl) == Control):
            self.selectedPolygon = self.clickedControl.parent
        elif(type(self.clickedControl) == Polygon):
            self.selectedPolygon = self.clickedControl
        else:
            self.selectedPolygon = None

    def updateControlRadius(self):
        for control in Control.instances:
            control.radius = control._radius / self.scale

    def checkIfClickedOnControl(self):
        scaledMousePos = self.scaleMousePos()

        for control in Control.instances:
            if(control.checkClicked(scaledMousePos)):
                return control
        return None

    def checkIfHoveringOverControl(self, scaledPos):

        if(self.hideControls):
            if(self.selectedPolygon is not None):
                for control in self.selectedPolygon.controls:
                    if(control.checkClicked(scaledPos)):
                        return control
        else:
            for control in Control.instances:
                if(control.checkClicked(scaledPos)):
                    return control

        for poly in self.polygons:
            if(pointInsidePolygon(scaledPos, poly.toList())):
                return poly

        return None

    def setPainterQuality(self):
        self.painter.setRenderHint(QPainter.Antialiasing, True)
        self.painter.setRenderHint(QPainter.HighQualityAntialiasing)
        self.painter.setRenderHint(QPainter.SmoothPixmapTransform)
        self.painter.setPen(Qt.NoPen) 

    def sizeHint(self):
        if(self.pixmap):
            return self.scale * self.pixmap.size()

    def offsetToCenter(self):
        #https://github.com/tzutalin/labelImg/blob/master/libs/canvas.py
        self.scale
        area = super(Canvas, self).size()
        w = self.pixmap.width() * self.scale
        h = self.pixmap.height() * self.scale

        aw = area.width()
        ah = area.height()

        x = (aw - w) / (2 * self.scale)
        y = (ah - h) / (2 * self.scale)

        return QPointF(x, y)

    def resizedParent(self):
        self.updateCanvasGlobalParameters()

    def scaleMousePos(self):
        offset = self.getCanvasStartPosition()

        mouseX = self.mousePos.x()
        mouseY = self.mousePos.y()

        scaledX = scale(mouseX, self.canvasGlobalLeft, self.canvasGlobalRight, 0, self.pixmap.width())
        scaledY = scale(mouseY, self.canvasGlobalTop, self.canvasGlobalBottom, 0, self.pixmap.height())

        scaledX = clamp(scaledX, 0, self.pixmap.width())
        scaledY = clamp(scaledY, 0, self.pixmap.height())

        return QPoint(scaledX, scaledY)

    def getCanvasStartPosition(self):
        parentCenterX = self.parent().size().width() // 2
        parentCenterY = self.parent().size().height() // 2

        startX = (parentCenterX - (self.canvasWidth // 2)) - self.hBar.value()
        startY = (parentCenterY - (self.canvasHeight // 2)) - self.vBar.value()

        return QPoint(startX, startY)

    def updateCanvasGlobalParameters(self):

        self.parentCenterX = self.parent().size().width() // 2
        self.parentCenterY = self.parent().size().height() // 2

        self.canvasCenterX = self.pixmap.width() // 2
        self.canvasCenterY = self.pixmap.height() // 2

        self.canvasWidth = int(self.pixmap.width() * self.scale)
        self.canvasHeight = int(self.pixmap.height() * self.scale)

        self.canvasGlobalLeft = self.parentCenterX - (self.canvasWidth // 2)
        self.canvasGlobalTop = self.parentCenterY - (self.canvasHeight // 2)

        if(self.canvasGlobalLeft < 0):
            self.canvasGlobalLeft = 0

        if(self.canvasGlobalTop < 0):
            self.canvasGlobalTop = 0

        self.canvasGlobalRight = self.canvasGlobalLeft + self.canvasWidth
        self.canvasGlobalBottom = self.canvasGlobalTop + self.canvasHeight

    def addPolygon(self, color):
        if(not self.pixmap.isNull()):

            polyColor = None

            if(type(color) is str):
                polyColor = QColor(int(color, 0))
            elif(type(color) is QColor):
                polyColor = color

            poly = Polygon(color=polyColor, 
                    center=QPoint(self.canvasCenterX, self.canvasCenterY))
            poly.computeBoundingBox()
            self.polygons.append(poly)

            self.updateControlRadius()
            self.update()
        else:
            QMessageBox.information(self, NO_IMAGE_TITLE, NO_IMAGE_TEXT)
    
    def deletePolygon(self):
        if(self.selectedPolygon is not None):
            try:
                index = self.polygons.index(self.selectedPolygon)
                self.polygons.pop(index)
                self.selectedPolygon = None
                self.update()
            except ValueError:
                pass

    def addControlToSelectedPolygon(self):
        if(self.selectedPolygon is not None):
            self.selectedPolygon.addControl()
            self.update()
            self.updateControlRadius()

    def deleteControlFromSelectedPolygon(self):
        if(self.selectedPolygon is not None):
            self.selectedPolygon.deleteLastControl()
            if(len(self.selectedPolygon.controls) <= 0):
                index = self.polygons.index(self.selectedPolygon)
                self.polygons.pop(index)
                self.selectedPolygon = None

            self.update()

    def resetCanvas(self):
        Control.deleteAllControls()
        self.highlightedControl = None
        self.selectedPolygon = None
        self.clickedControl = None
        self.polygons = []

    def loadImage(self, filename, copyPolygons=False):
        self.pixmap.load(filename)
        self.filenamePrefix = filename[:-4]

        pickleFilename = f"{self.filenamePrefix}{POLYGON_SUFFIX}"
        
        if(os.path.exists(pickleFilename)):
            self.resetCanvas()
            with open(pickleFilename, 'rb') as polyPickle:
                polygons = pickle.load(polyPickle)
                for polygon in polygons:
                    color = polygon['color']
                    newPolygon = Polygon(color=QColor(color[0], color[1], color[2]))
                    newPolygon.setFromListOfCotnrolPositions(polygon['controls'])
                    
                    newPolygon.updateParameters()
                    newPolygon.updateOffsets()
                    self.polygons.append(newPolygon)
        elif(copyPolygons is False):
            self.resetCanvas()

        self.updateControlRadius()
        self.updateCanvasGlobalParameters()
        self.update()

    def saveImage(self):
        if(not self.pixmap.isNull()):
            image = np.zeros((self.pixmap.height(),self.pixmap.width(), 3), dtype=np.uint8)
            polygons = []
            for polygon in self.polygons:
                polyToDraw = np.array(polygon.toList())
                color = polygon.colorToCV()

                image = cv2.fillPoly(image, [polyToDraw], color)

                polyObj = {'color': color, 'controls': polyToDraw}
                polygons.append(polyObj)

            #Deals with openCV using BGR instead of RGB
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            cv2.imwrite(f"{self.filenamePrefix}{SEGMENTATION_SUFFIX}", image)

            with open(f"{self.filenamePrefix}{POLYGON_SUFFIX}", 'wb+') as polyPickle:
                pickle.dump(polygons, polyPickle)

    def setState(self, state):
        self.state = state

        if(state == DRAW_POLYGON):
            self.freeDrawPolygon = None
            self.highlightedControl = None
            self.closestLine = None
            self.selectedPolygon = None
        else:
            self.freeDrawPolygon = None

        if(not self.pixmap.isNull()):
            self.update()

    def setColor(self, color):
        if(type(color) == str):
            self.color = QColor(color)
        elif(type(color) == QColor):
            self.color = color

    def getClosestLineIntersection(self):
        pos1 = self.selectedPolygon.controls[self.closestLine[0]].position
        pos2 = self.selectedPolygon.controls[self.closestLine[1]].position
        line = [pos1.x(), pos1.y(), pos2.x(), pos2.y()]

        mPos = self.scaleMousePos()

        vLine = [mPos.x(), mPos.y() + MOUSE_SEARCH_AREA, mPos.x(), mPos.y() - MOUSE_SEARCH_AREA] 
        hLine = [mPos.x() - MOUSE_SEARCH_AREA, mPos.y(), mPos.x() + MOUSE_SEARCH_AREA, mPos.y()]

        intersectionV = linesIntersect(line, vLine)
        intersectionH = linesIntersect(line, hLine)

        intersection = intersectionV

        if(intersectionV is not None and intersectionH is not None):
            vDistance = distance([intersectionV['x'], intersectionV['y']], [mPos.x(), mPos.y()])
            hDistance = distance([intersectionH['x'], intersectionH['y']], [mPos.x(), mPos.y()])

            if(vDistance < hDistance):
                intersection = intersectionV
            else:
                intersection = intersectionH
        elif(intersectionV is None):
            intersection = intersectionH

        if(intersection is not None):
            return QPoint(intersection['x'], intersection['y'])
        else:
            return QPoint(OFFSCREEN, OFFSCREEN)

    def copyPolygon(self):
        if(self.selectedPolygon is not None):
            self.copyOfSelectedPolygon = self.selectedPolygon

    def pastePolygon(self):
        if(self.copyOfSelectedPolygon is not None):
            import time
            startTime = time.time()
            c = self.copyOfSelectedPolygon

            newPolygon = Polygon(color=QColor(c.color))
            newPolygon.copyControls(c.controls, offset=COPY_OFFSET)
            newPolygon.updateParameters()
            self.polygons.append(newPolygon)

            self.updateControlRadius()
            self.update()

    def askForColorChange(self):
        if(self.selectedPolygon is not None):
            color = QColorDialog.getColor()

            if(QColor.isValid(color)):
                self.setColor(color)
                self.selectedPolygon.setColor(color)

    def changeHideControlsState(self, state):
        if(state > 0):
            self.hideControls = True
        else:
            self.hideControls = False

        self.update()