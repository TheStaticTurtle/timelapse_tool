from . import Plugin
from datetime import datetime
import cv2

class PluginMonitor(Plugin):
	NAME="Monitor"
	def __init__(self, name=NAME):
		Plugin.__init__(self,name=name)
		self.font = cv2.FONT_HERSHEY_SIMPLEX
		self.frame=None

	def setup(self, plugins=[], size=(0,0), capture=None, capture_dir=""):
		Plugin.setup(self, plugins=plugins, size=size, capture=capture, capture_dir=capture_dir)
		cv2.namedWindow("Monitor: "+self.name,cv2.WINDOW_NORMAL)

	def write_txt(self, img, x, y, txt, font, size, thick, color):
		cv2.putText(img, txt, (x, y), font, size, color, thick, cv2.LINE_AA)
		return x + cv2.getTextSize(txt, font, size, thick)[0][0] + 10, y

	def process_monitor(self, img):
		counter=0
		txt = datetime.now().strftime('%H:%M:%S')
		self.write_txt(img, 10, 45, txt, self.font, 1.5, 5, (255,255,255))
		self.write_txt(img, 10, 45, txt, self.font, 1.5, 2, (24, 175, 240))
		
		x,y = self.write_txt(img, 10, 710, "Frame counts:", self.font, 0.7, 1, (252, 128, 3))
		for plugin in self.plugins:
			if plugin.frame_counter is not None:
				txt = "%s: %r" % (plugin.name, plugin.frame_counter)
				color = (24, 240, 150) if plugin.working else (3, 57, 252)
				x,y = self.write_txt(img, x, y, txt, self.font, 0.6, 1, color)

		x,y = self.write_txt(img, 10, 685, "GPS:", self.font, 0.7, 1, (252, 128, 3))
		for plugin in self.plugins:
			if plugin.gps is not None:
				txt = "%s: lat=%f lon=%f %dm %ds" % (plugin.name, plugin.gps[0], plugin.gps[1], plugin.altitude, plugin.sec_since_last_update)
				color = (24, 240, 150) if plugin.working else (3, 57, 252)
				x,y = self.write_txt(img, x, y, txt, self.font, 0.6, 1, color)

		self.frame = img.copy()
		return img

	def monitor(self, img_monitor, img_processed, img):
		cv2.namedWindow("Monitor: "+self.name,cv2.WINDOW_NORMAL)
		cv2.imshow("Monitor: "+self.name, self.frame)