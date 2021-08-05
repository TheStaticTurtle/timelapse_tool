from . import Plugin, get_plugins_after_plugin, filecount_for_dir
from datetime import datetime
import cv2
import time
import socket
import io
import pynmea2
import math
import exif
from exif import DATETIME_STR_FORMAT

class PluginEXIFTool(Plugin):
	NAME = "ExifTool"
	def __init__(self, make=None, copyright=None, model=None, image_description_prepend=None, name=NAME):
		Plugin.__init__(self,name=name)
		self.model = model
		self.make = make
		self.copyright = copyright
		self.image_description_prepend = image_description_prepend

	def process_photo(self, file_path, image_description=None):
		with open(file_path, 'rb') as image_file:
			img = exif.Image(image_file)

		img.date_time = datetime.now().strftime(DATETIME_STR_FORMAT)

		if self.model:
			img.model = self.model
		if self.make:
			img.make = self.make
		else:
			img.make = "TimelapseTool"

		if self.copyright:
			img.copyright = self.copyright
		if self.image_description_prepend:
			p = img.get("image_description")
			img.image_description = self.image_description_prepend + " " + (p if p else "")

		with open(file_path, 'wb') as updated_image_file:
		    updated_image_file.write(img.get_file())
		return True
