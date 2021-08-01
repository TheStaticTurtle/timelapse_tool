from . import Plugin, get_plugins_after_plugin, filecount_for_dir
from datetime import datetime
import cv2
import time
import glob, parse

class PluginManualCapture(Plugin):
	NAME = "ManualCapture"
	def __init__(self, directory, file_format, key, name=NAME):
		Plugin.__init__(self,name=name)

		self.key = key
		self.directory = directory
		self.file_format = file_format

		self.counter = filecount_for_dir(file_format, directory)
		self.tlast = 0

		self.frame = None
		
	@property
	def frame_counter(self):
		return self.counter

	def write_file(self, img_monitor, img_processed, img):
		self.frame = img_processed

	def onkeypress(self, key):
		if key == self.key:
			self.log.info("Saving at: "+self.directory + self.file_format.format(self.counter))

			cv2.imwrite(self.directory + self.file_format.format(self.counter), self.frame)
		
			for plugin in get_plugins_after_plugin(self, self.plugins):
				plugin.process_photo(self.directory + self.file_format.format(self.counter))
			
			self.counter += 1
			self.tlast = time.time()
