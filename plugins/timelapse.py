from . import Plugin, get_plugins_after_plugin, filecount_for_dir
from datetime import datetime
import cv2
import time

from pathlib import Path

class PluginTimelapse(Plugin):
	NAME = "Timelapse"
	def __init__(self, directory, file_format, interval, name=NAME):
		Plugin.__init__(self,name=name)

		self.directory = directory
		self.file_format = file_format
		self.interval = interval

		self.counter = filecount_for_dir(file_format, directory)
		self.tlast = 0
		self.frame = None

	def setup(self, plugins=[], size=(0,0), capture=None, capture_dir=""):
		Plugin.setup(self, plugins=plugins, size=size, capture=capture, capture_dir=capture_dir)
		Path(self.directory).mkdir(parents=True, exist_ok=True)

	@property
	def frame_counter(self):
		return self.counter

	def process(self, img):
		self.log.debug("here")
		self.frame = img
		return img

	def write_file(self, img_monitor, img_processed, img):
		if time.time() > (self.tlast + self.interval):
			self.log.info("Saving at: "+self.directory + self.file_format.format(self.counter))

			cv2.imwrite(self.directory + self.file_format.format(self.counter), self.frame)
		
			for plugin in get_plugins_after_plugin(self, self.plugins):
				plugin.process_photo(self.directory + self.file_format.format(self.counter))
			
			self.counter += 1
			self.tlast = time.time()
