import os
from libs.Constants import *

class FolderLoader:
	def __init__(self):
		self.folderPath = ""
		self.imagesInFolder = []
		self.index = 0

	def getNextImageFilename(self):
		if(len(self.imagesInFolder) > 0):
			self.index += 1

			if(self.index >= len(self.imagesInFolder)):
				self.index = len(self.imagesInFolder) - 1

			return self.imagesInFolder[self.index]
		else:
			return None

	def getPreviousImageFilename(self):
		if(len(self.imagesInFolder) > 0):
			self.index -= 1

			if(self.index < 0):
				self.index = 0

			return self.imagesInFolder[self.index]
		else:
			return None

	def loadFolder(self, folderPath):
		self.folderPath = folderPath
		filesInFolder = os.listdir(folderPath)
		self.index = 0
		imageFilepaths = []
		files = os.listdir(folderPath)

		for filename in files:
		    if any(x in filename for x in OPEN_FOLDER_FILTERS) and not SEGMENTATION_SUFFIX in filename:
		        imageFilepaths.append(f"{folderPath}/{filename}")

		self.imagesInFolder = imageFilepaths
		self.index = 0
		return self.imagesInFolder[self.index]

	def loadSingleFile(self, filename):
		self.folderPath = filename
		self.imagesInFolder = [filename]
