from . import Plugin, get_plugins_before_plugin, filecount_for_dir
from datetime import datetime
import cv2
import time

from pathlib import Path

class PluginVideoCapture(Plugin):
	NAME = "VideoCapture"
	def __init__(self, directory, file_format, key, name=NAME):
		Plugin.__init__(self,name=name)

		self.key = key
		self.directory = directory
		self.file_format = file_format

		self.counter = filecount_for_dir(file_format, directory)
		self.tlastfps = time.time()
		self.tlastfc = 0

		self.frame = None
		self.fps = 25
		self.shape = (1920,1080)
		self.recorder = None

	def setup(self, plugins=[], size=(0,0), capture=None, capture_dir=""):
		Plugin.setup(self, plugins=plugins, size=size, capture=capture, capture_dir=capture_dir)
		Path(self.directory).mkdir(parents=True, exist_ok=True)
		self.tlastfps = time.time()

	@property
	def frame_counter(self):
		return self.counter

	@property
	def working(self):
		return self.recorder is not None

	def process_monitor(self, img):
		cv2.circle(img,(1235,45), 25, (255,255,255), -1)
		if self.recorder is not None:
			cv2.circle(img,(1235,45), 20, (0,0,255), -1)
		else:
			cv2.circle(img,(1235,45), 20, (128,128,128), -1)
		return img

	def process(self, img):
		self.tlastfc+=1
		if self.tlastfps +2 < time.time():
			self.fps = int(self.tlastfc / 2.0)
			self.tlastfc = 0
			self.tlastfps = time.time()
			self.log.debug("Calculated fps: %d" % self.fps)

		self.shape = img.shape[:2][::-1]

		if self.recorder is not None:
			self.recorder.write(img)
		return img

	def onkeypress(self, key):
		if key == self.key:
			if self.recorder is None:
				self.log.info("Starting to record at: "+self.directory + self.file_format.format(self.counter))
				self.recorder = cv2.VideoWriter(
					self.directory + self.file_format.format(self.counter),
					cv2.VideoWriter_fourcc(*"XVID"), 
					self.fps, 
					self.shape
				)
			else:
				self.log.info("Stoping to record at: "+self.directory + self.file_format.format(self.counter))
				self.recorder.release()
				for plugin in get_plugins_before_plugin(self, self.plugins):
					plugin.process_video(self.directory + self.file_format.format(self.counter))
				self.counter += 1
				self.recorder = None

	def quit(self):
		if self.recorder is not None:
			self.recorder.release()