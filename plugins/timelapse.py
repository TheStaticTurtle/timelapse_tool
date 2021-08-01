from . import Plugin, get_plugins_after_plugin
from datetime import datetime
import cv2
import time
import glob, parse

def filecount_for_dir(search_format, directory):
	try:
		count = max([x[0] for x in [parse.parse(search_format, os.path.basename(x)) for x in glob.glob(directory+"*")] if x])
	except ValueError as e:
		return 0

class PluginTimelapse(Plugin):
	NAME = "Timelapse"
	def __init__(self, directory, file_format, interval, name=NAME):
		Plugin.__init__(self,name=name)

		self.directory = directory
		self.file_format = file_format
		self.interval = interval

		self.counter = filecount_for_dir(file_format, directory)
		self.tlast = 0

	@property
	def frame_counter(self):
		return self.counter

	def write_file(self, img_monitor, img_processed, img):
		if time.time() > (self.tlast + self.interval):
			self.log.info("Saving at: "+self.directory + self.file_format.format(self.counter))

			cv2.imwrite(self.directory + self.file_format.format(self.counter), img_processed)
		
			for plugin in get_plugins_after_plugin(self, self.plugins):
				plugin.process_photo(self.directory + self.file_format.format(self.counter))
			
			self.counter += 1
			self.tlast = time.time()
