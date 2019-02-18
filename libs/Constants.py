from PyQt5.QtGui import QIcon

#Main Window
# -------------------------------------------------- #
WINDOW_NAME = 'Polygon Annotator'
MAIN_ICON = 'icons/main_icon.png'

DEFAULT_X = 500
DEFAULT_Y = 100
DEFAULT_WIDTH = 1280
DEFAULT_HEIGHT = 720

NOT_SAVED_TITLE = "Attention"
NOT_SAVED_TEXT = "Unsaved file, continue?"

#Theme
# -------------------------------------------------- #
BACKGROUND_COLOR = "rgb(40, 41, 35, 255)"
HIGHLIGHT_COLOR = "rgba(50, 50, 45, 255)"

TEXT_COLOR = "white"
FONT = "monospace"

FONT_SIZE = "15px"
FILE_LIST_HIGHLIGHTED_COLOR = "rgb(0, 255, 255, 255)"
STYLE_SHEET = f'''
		QWidget {{
			color: {TEXT_COLOR}; 
		    background-color: {BACKGROUND_COLOR};
		    font-family: {FONT};
		    font-size: {FONT_SIZE};
		}}

	    QMenu::item:selected {{
			background-color: {HIGHLIGHT_COLOR};
		}}

		QMenu::item:disabled {{
		    color: gray;
		}}

		QListView::item {{
			background-color:{BACKGROUND_COLOR};
		}}

		QListView::item:selected {{
			background-color: {FILE_LIST_HIGHLIGHTED_COLOR};
		}}

		QCheckBox {{
		    padding-top: 10px;
    		padding-bottom: 5px;
		}}

		QCheckBox::indicator {{
    		subcontrol-position: top center;
    	}}

    	QComboBox {{
			background-color: rgb(0, 255, 0);
			selection-background-color: rgba(0,0,0,0);
		}}

    '''
#STYLE_SHEET = ""

#Control Constants
# -------------------------------------------------- #
CONTROL_RADIUS = 10
CONTROL_DEFAULT_COLOR = 0x00FF00
CONTROL_HIGHLIGHT_COLOR = 0xFFFFFF
CONTROL_SELECTED_COLOR = 0xFFFF00
CONTROL_MIN_LINE_DISTANCE = 12
MOUSE_SEARCH_AREA = 20
COPY_OFFSET = 10

#Polygon Constants
# -------------------------------------------------- #
NUM_CONTROLS = 4
POLYGON_SIZE = 50
POLYGON_START = 150

#States
# -------------------------------------------------- #
MOVE_CONTROLS = 1
DRAW_POLYGON = 2
ADD_CONTROL = 3

#Canvas Constants
# -------------------------------------------------- #
ZOOM_INCREMENT = 0.1
CONTROL_OPACITY = 0.3
HIGHLIGHTED_OPACITY = 0.5
SELECTED_OPACITY = 0.3
DEFAULT_SCALE = 1
CANVAS_DEFAULT_COLOR = 0x00FF00
MOUSE_TARGET_THICKNESS = 30
MIN_SCALE = 1
MAX_SCALE = 5

NO_IMAGE_TITLE = "No Image"
NO_IMAGE_TEXT = "No image, please load an image"

SEGMENTATION_SUFFIX = "_SEGMENT.png"
POLYGON_SUFFIX = "_POLYGONS.pickle"

CLOSEST_LINE_COLOR = 0xFF0000

#Menus
# -------------------------------------------------- #
FILE_MENU_TEXT = "File"
EDIT_MENU_TEXT = "Edit"
HELP_MENU_TEXT = "Help"

#Open File
# -------------------------------------------------- #
OPEN_FILE_TEXT = "Open File"
OPEN_FILE_SHORTCUT = "Ctrl+O"
OPEN_FILE_DIALOG_TEXT = "Open File"
OPEN_FILE_DIALOG_FILTER = "Images (*.png *.jpg)"

#Open Folder
# -------------------------------------------------- #
OPEN_FOLDER_TEXT = "Open Folder"
OPEN_FOLDER_SHORTCUT = "Ctrl+Shift+O"
OPEN_FOLDER_DIALOG_TEXT = "Open Folder"
OPEN_FOLDER_FILTERS = ['.jpg', '.png']

#Open Folder
# -------------------------------------------------- #
SAVE_TEXT = "Save"
SAVE_SHORTCUT = "Ctrl+S"

#Copy
# -------------------------------------------------- #
COPY_TEXT = "Copy"
COPY_SHORTCUT = "Ctrl+C"

#Paste 
# -------------------------------------------------- #
PASTE_TEXT = "Paste"
PASTE_SHORTCUT = "Ctrl+V"

#How To Use
# -------------------------------------------------- #
HOW_TO_USE_TEXT = "How to use"

#Toolbar Menu
# -------------------------------------------------- #
TOOLBAR_NAME = "Toolbar"

POLY_COLORS_TEXT = ["Green", "Red", "Blue", "Yellow", "Purple", "Light Blue", "Orange"]
POLY_COLORS = ["0x00FF00", "0xFF0000", "0x0000FF", "0xFFFF00", "0xFF00FF", "0x00FFFF", "0xFFA500"]
POLY_COLORS_STYLE = ["#00FF00", "#FF0000", "#0000FF", "#FFFF00", "#FF00FF", "#00FFFF", "#FFA500"]
POLY_SHORTCUTS = ["1", "2", "3"]

CUSTOM_COLOR_TEXT = "Custom Color"
CUSTOM_COLOR_SHROTCUT = ""
CUSTOM_COLOR_ICON = "icons/custom_color.png"
CUSTOM_COLOR_TOOLTIP = "Select custom color of next polygon"

CHANGE_COLOR_TEXT = "Change Color"
CHANGE_COLOR_SHROTCUT = ""
CHANGE_COLOR_ICON = "icons/change_color.png"
CHANGE_COLOR_TOOLTIP = "Change color of selected polygon"

DRAW_POLYGON_TEXT = "Draw Polygon"
DRAW_POLYGON_SHORTCUT = "w"
DRAW_POLYGON_ICON = "icons/draw_polygon.png"
DRAW_POLYGON_TOOLTIP = '''Free draw a polygon on the image. \nColor is determined using either \npolygon color dropdown color or custom color'''

DELETE_POLYGON_TEXT = "Delete Polygon"
DELETE_POLYGON_SHORTCUT = "del"
DELETE_POLYGON_ICON = "icons/delete_polygon.png"
DELETE_POLYGON_TOOLTIP = "Delete selected polygon"

ADD_CONTROL_TEXT = "Add Control"
ADD_CONTROL_SHORTCUT = ""
ADD_CONTROL_ICON = "icons/add_control.png"
ADD_CONTROL_TOOLTIP= "Add control to selected polygon"

DELETE_CONTROL_TEXT = "Delete Control"
DELETE_CONTROL_SHORTCUT = "q"
DELETE_CONTROL_ICON = "icons/delete_control.png"
DELETE_CONTROL_TOOLTIP = "Delete last control from selected polygon"

NEXT_IMAGE_TEXT = "Next Image"
NEXT_IMAGE_SHORTCUT = "d"
NEXT_IMAGE_ICON = "icons/next.png"
NEXT_IMAGE_TOOLTIP = "Load next image in folder"

PREVIOUS_IMAGE_TEXT = "Previous Image"
PREVIOUS_IMAGE_SHORTCUT = "a"
PREVIOUS_IMAGE_ICON = "icons/prev.png"
PREVIOUS_IMAGE_TOOLTIP = "Load previous image in folder"

FREE_DRAW_TEXT = "Free Draw"

COPY_POLGONS_FOR_NEXT_IMAGE = "Copy Polygons"
HIDE_CONTROLS_TEXT = "Hide Controls"

#File Dock
# -------------------------------------------------- #
FILE_DOCK_TITLE = "File List"

EMPTY = ""

#Keys
# -------------------------------------------------- #
NUMBERS = [str(x + 1) for x in range(len(POLY_COLORS))]

#Settings filenames
# -------------------------------------------------- #
COLOR_CLASSES_FILENAME = "data/settings.txt"

#Load user settings
# -------------------------------------------------- #
import os
if(os.path.exists(COLOR_CLASSES_FILENAME)):

	POLY_COLORS_TEXT = []
	POLY_COLORS = []
	POLY_COLORS_STYLE = []
	POLY_SHORTCUTS = []

	index = 1

	with open(COLOR_CLASSES_FILENAME, 'r') as colorClasses:
		text = colorClasses.read()
		classes = text.split("\n")
		for c in classes:
			if(c == EMPTY or "[" in c):
				continue

			split = c.split(":")
			name = split[0]
			value = split[1]

			POLY_COLORS_TEXT.append(name)
			POLY_COLORS_STYLE.append(value)
			POLY_COLORS.append(value.replace('#', '0x'))
			POLY_SHORTCUTS.append(index)

			index += 1

#Random
# -------------------------------------------------- #

OFFSCREEN = 100000
SCROLL_SCALE = 2