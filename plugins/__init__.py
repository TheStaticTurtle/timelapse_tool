import logging
import glob
import parse
import os

__all__ = ["effects"]

def get_plugins_after_plugin(plugin, plugins):
	return plugins[plugins.index(plugin)+1:]

def get_plugins_before_plugin(plugin, plugins):
	return plugins[:plugins.index(plugin)]


def filecount_for_dir(search_format, directory):
	try:
		count = max([x[0] for x in [parse.parse(search_format, os.path.basename(x)) for x in glob.glob(directory+"*")] if x])
		return count
	except ValueError as e:
		return 0


class Plugin(object):
	NAME = "GenricPlugin"

	"""docstring for Plugin"""
	def __init__(self,name=NAME):
		super(Plugin, self).__init__()
		self.name= name
		self.size = (0,0)
		self.capture = None
		self.plugins = []
		self.capture_dir = ""
		self.log = logging.getLogger(name)
		self._working = True

	@property
	def frame_counter(self):
		return None

	@property
	def gps(self):
		return None

	@property
	def working(self):
		return self._working
	
	def setup(self, plugins=[], size=(0,0), capture=None, capture_dir=""):
		self.size = size
		self.plugins = plugins
		self.capture = capture
		self.capture_dir = capture_dir

	def process(self, img):
		return img

	def process_monitor(self, img):
		return img

	def monitor(self, img_monitor, img_processed, img):
		pass

	def write_file(self, img_monitor, img_processed, img):
		pass

	def process_photo(self, file_path, image_description=None):
		return False

	def process_video(self, file_path):
		return False

	def onkeypress(self, key):
		pass

	def quit(self):
		pass