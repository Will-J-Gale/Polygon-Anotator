import sys

from PyQt5.QtWidgets import QMainWindow, QScrollArea, QToolBar, QLabel, \
QStatusBar, QCheckBox, QComboBox, QListWidgetItem, QAction, QVBoxLayout, \
QVBoxLayout, QFileDialog, QMessageBox, QDockWidget, QListWidget

from PyQt5.QtGui import QIcon, QColor

from PyQt5.QtCore import QSignalMapper, QPoint
from libs.Canvas import *
from libs.Constants import *
import math
import os
from libs.FolderLoader import FolderLoader

class Window(QMainWindow):
    
    def __init__(self, x=DEFAULT_X, y=DEFAULT_Y, w=DEFAULT_WIDTH, h=DEFAULT_HEIGHT):
        super(Window, self).__init__()
        self.setGeometry(x, y, w, h)
        self.setWindowTitle(WINDOW_NAME)
        self.setWindowIcon(QIcon(MAIN_ICON))
        self.home()

    def home(self):

        self.folderLoader = FolderLoader()

        self.saved = True

        #Parameters
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)

        self.createMainMenu()

        self.canvas = Canvas(parent=self)

        self.scrollArea = QScrollArea()
        self.scrollArea.setWidget(self.canvas)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setStyleSheet(STYLE_SHEET)

        self.labelCoordinates = QLabel('')
        self.statusBar.addPermanentWidget(self.labelCoordinates)

        self.toolbar = QToolBar(TOOLBAR_NAME, self)
        self.toolbar.setStyleSheet(STYLE_SHEET)
        self.toolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.addToolBar(Qt.LeftToolBarArea, self.toolbar)

        self.mapper = QSignalMapper()
        self.createColorComboBox()
        self.createToolbarActions()
        self.createFileDock()

        self.setCentralWidget(self.scrollArea)
        self.update()
        self.showMaximized()

    def createMainMenu(self):

        #Main Menu
        mainMenu = self.menuBar()
        fileMenu = mainMenu.addMenu(FILE_MENU_TEXT)
        editMenu = mainMenu.addMenu(EDIT_MENU_TEXT)
        helpMenu = mainMenu.addMenu(HELP_MENU_TEXT)

        #File Menu Actions
        openFileAction = self.createAction(OPEN_FILE_TEXT, OPEN_FILE_SHORTCUT, self.openFile)
        openFolderAction = self.createAction(OPEN_FOLDER_TEXT, OPEN_FOLDER_SHORTCUT, self.openFolder)
        saveAction = self.createAction(SAVE_TEXT, SAVE_SHORTCUT, self.save)

        fileMenu.addActions([openFileAction, openFolderAction, saveAction])

        #Edit Menu Actions
        copyAction = self.createAction(COPY_TEXT, COPY_SHORTCUT, self.copy)
        pasteAction = self.createAction(PASTE_TEXT, PASTE_SHORTCUT, self.paste)

        editMenu.addActions([copyAction, pasteAction])

        #Help Menu Actions
        howToUseAction = self.createAction(HOW_TO_USE_TEXT, EMPTY, self.howToUse)
        helpMenu.addActions([howToUseAction])

    def createToolbarActions(self):
        
        self.toolbar.addSeparator()

        #Polygons
        drawPolygonAction = self.createActionWithIcon(DRAW_POLYGON_ICON, 
                                DRAW_POLYGON_TEXT, 
                                DRAW_POLYGON_SHORTCUT, 
                                self.setDrawingState,
                                DRAW_POLYGON_TOOLTIP)

        deletePolygonAction = self.createActionWithIcon(DELETE_POLYGON_ICON, 
                                DELETE_POLYGON_TEXT, 
                                DELETE_POLYGON_SHORTCUT,
                                self.canvas.deletePolygon,
                                DELETE_POLYGON_TOOLTIP)

        self.toolbar.addActions([drawPolygonAction, deletePolygonAction])
        self.toolbar.addSeparator()

        ##Controls
        addControlAction = self.createActionWithIcon(ADD_CONTROL_ICON, 
                                ADD_CONTROL_TEXT, 
                                ADD_CONTROL_SHORTCUT,
                                self.canvas.addControlToSelectedPolygon,
                                ADD_CONTROL_TOOLTIP)

        deleteControlAction = self.createActionWithIcon(DELETE_CONTROL_ICON, 
                                DELETE_CONTROL_TEXT, 
                                DELETE_CONTROL_SHORTCUT,
                                self.canvas.deleteControlFromSelectedPolygon,
                                DELETE_CONTROL_TOOLTIP)

        self.toolbar.addActions([addControlAction, deleteControlAction])
        self.toolbar.addSeparator()

        nextImageAction = self.createActionWithIcon(NEXT_IMAGE_ICON, 
                                NEXT_IMAGE_TEXT, 
                                NEXT_IMAGE_SHORTCUT,
                                self.nextImage,
                                NEXT_IMAGE_TOOLTIP)

        previousImageAction = self.createActionWithIcon(PREVIOUS_IMAGE_ICON, 
                                PREVIOUS_IMAGE_TEXT, 
                                PREVIOUS_IMAGE_SHORTCUT,
                                self.previousImage,
                                PREVIOUS_IMAGE_TOOLTIP)

        self.toolbar.addActions([nextImageAction, previousImageAction])

        self.copyPolygonsCheckbox = QCheckBox()
        self.copyPolygonsCheckbox.setStyleSheet(STYLE_SHEET)
        self.toolbar.addWidget(self.copyPolygonsCheckbox)

        copyPolygonsLabel = QLabel(COPY_POLGONS_FOR_NEXT_IMAGE)
        copyPolygonsLabel.setAlignment(Qt.AlignCenter)
        self.toolbar.addWidget(copyPolygonsLabel)

        self.hideControlsCheckBox = QCheckBox()
        self.hideControlsCheckBox.setStyleSheet(STYLE_SHEET)
        self.hideControlsCheckBox.stateChanged.connect(self.canvas.changeHideControlsState)
        self.toolbar.addWidget(self.hideControlsCheckBox)

        hideControlsLabel = QLabel(HIDE_CONTROLS_TEXT)
        hideControlsLabel.setAlignment(Qt.AlignCenter)
        self.toolbar.addWidget(hideControlsLabel)

    def createColorComboBox(self):
        colorLabel = QLabel("Polygon Color")
        colorLabel.setAlignment(Qt.AlignCenter)
        self.toolbar.addWidget(colorLabel)

        self.colorComboBox = QComboBox()
        self.colorComboBox.setStyleSheet(STYLE_SHEET)
        self.colorComboBox.activated[int].connect(self.changeColor)
        self.toolbar.addWidget(self.colorComboBox)
        model = self.colorComboBox.model()

        for i in range(len(POLY_COLORS_TEXT)):
            colorText = POLY_COLORS_TEXT[i]
            colorStyle = POLY_COLORS_STYLE[i]
            item = QStandardItem(colorText)
            item.setBackground(QColor(colorStyle))
            item.setData(colorStyle)
            model.appendRow(item)

        self.customColor = self.createActionWithIcon(CUSTOM_COLOR_ICON, CUSTOM_COLOR_TEXT, EMPTY, self.addCustomColor, CUSTOM_COLOR_TOOLTIP)
        self.toolbar.addAction(self.customColor)

        self.changeColor = self.createActionWithIcon(CHANGE_COLOR_ICON, CHANGE_COLOR_TEXT, EMPTY, self.canvas.askForColorChange, CHANGE_COLOR_TOOLTIP)
        self.toolbar.addAction(self.changeColor)

    def createFileDock(self):
        self.fileDock = QDockWidget(FILE_DOCK_TITLE, self)

        self.fileListWidget = QListWidget()
        self.fileListWidget.setStyleSheet(STYLE_SHEET)
        self.fileListWidget.itemDoubleClicked.connect(self.fileItemChanged)
        fileListLayout = QVBoxLayout()
        fileListLayout.addWidget(self.fileListWidget)
        fileListContainter =  QWidget()
        fileListContainter.setLayout(fileListLayout)

        self.fileDock.setWidget(fileListContainter)
        self.fileDock.setStyleSheet(STYLE_SHEET)
        self.fileDock.setFeatures(QDockWidget.DockWidgetFloatable | 
                 QDockWidget.DockWidgetMovable)

        self.addDockWidget(Qt.RightDockWidgetArea, self.fileDock)

    def createAction(self, text, shortcut, triggered=None):
        action = QAction(text, self)
        action.setShortcut(shortcut)
        action.setToolTip(EMPTY)
        action.triggered.connect(triggered)

        return action

    def createActionWithIcon(self, iconPath, text, shortcut, triggered, tooltip=""):
        action = QAction(QIcon(iconPath), text, self)
        action.triggered.connect(triggered)
        action.setToolTip(tooltip)
        action.setShortcut(shortcut)

        return action

    def freeDrawCheckBoxChanged(self):
        if(self.freeDrawCheckbox.checkState() > 0):
            self.canvas.setState(FREE_DRAW)
        else:
            self.canvas.setState(MOVE_CONTROLS)

    def fileItemChanged(self):
        filepath = self.fileListWidget.selectedItems()[0].text()
        self.canvas.loadImage(filepath)


    def nextImage(self):
        if(self.checkContinue()):
            image = self.folderLoader.getNextImageFilename()
            if(image is not None):
                copyPolygons = self.copyPolygonsCheckbox.checkState() > 0
                self.canvas.loadImage(image, copyPolygons)
                self.saved = True

                fileWidgetItem = self.fileListWidget.item(self.folderLoader.index)
                if(fileWidgetItem is not None):
                    fileWidgetItem.setSelected(True)

    def previousImage(self):
        if(self.checkContinue()):
            image = self.folderLoader.getPreviousImageFilename()
            
            if(image is not None):
                self.canvas.loadImage(image)
                self.saved = True

                fileWidgetItem = self.fileListWidget.item(self.folderLoader.index)
                if(fileWidgetItem is not None):
                    fileWidgetItem.setSelected(True)

    def checkContinue(self):
        if(not self.saved):
            choice = QMessageBox.question(self, NOT_SAVED_TITLE,
                                                NOT_SAVED_TEXT)
            if(choice == QMessageBox.Yes):
                return True
            else:
                return False
        else:
            return True

    def addColoredPolygon(self, color):
        self.canvas.addPolygon(color)
        self.saved = False

    def addCustomColor(self):
        color = QColorDialog.getColor()

        if(QColor.isValid(color)):
            self.canvas.setColor(color)
            self.saved = False

    def calculateCenter(self):
        self.centerX = self.rect().width() // 2
        self.centerY = self.rect().height() // 2
        self.center = QPoint(self.centerX, self.centerY)
       
    def resizeEvent(self, event):
        self.calculateCenter()
        self.canvas.resizedParent()
        self.canvas.adjustSize()

    def keyPressEvent(self, event):
        if(event.key() == Qt.Key_Escape):
            self.canvas.setState(MOVE_CONTROLS)
        else:
            for number in NUMBERS:
                if(event.text() == number):
                    self.colorComboBox.setCurrentIndex(int(number) - 1)
                    self.colorComboBox.activated.emit(int(number) - 1)

    def openFile(self):
        filename, _ = QFileDialog.getOpenFileName(self, OPEN_FILE_DIALOG_TEXT, EMPTY, OPEN_FILE_DIALOG_FILTER)
        if any(x in filename for x in OPEN_FOLDER_FILTERS):
            self.folderLoader.loadSingleFile(filename)
            self.canvas.loadImage(filename)

    def openFolder(self):
        folder = QFileDialog.getExistingDirectory(self, OPEN_FOLDER_DIALOG_TEXT)
        if(folder is not EMPTY):
            firstImage = self.folderLoader.loadFolder(folder)
            self.canvas.loadImage(firstImage)

            for imagePath in self.folderLoader.imagesInFolder:
                self.fileListWidget.addItem(QListWidgetItem(imagePath))

    def save(self):
        self.saved = True
        self.canvas.saveImage()

    def setDrawingState(self):
        self.canvas.setState(DRAW_POLYGON)
        
    def changeColor(self, index):
        color = QColor(POLY_COLORS_STYLE[index])
        self.colorComboBox.setStyleSheet(f'background-color: {POLY_COLORS_STYLE[index]}')
        self.canvas.setColor(color)

    def howToUse(self):
        print("LINK TO WEBSITE")

    def copy(self):
        self.canvas.copyPolygon()

    def paste(self):
        self.canvas.pastePolygon()
    