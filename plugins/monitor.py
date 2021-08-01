from . import Plugin
from datetime import datetime
import cv2

class PluginMonitor(Plugin):
	NAME="Monitor"
	def __init__(self, name=NAME):
		Plugin.__init__(self,name=name)
		self.font = cv2.FONT_HERSHEY_SIMPLEX

	def setup(self, plugins=[], size=(0,0), capture=None, capture_dir=""):
		Plugin.setup(self, plugins=plugins, size=size, capture=capture, capture_dir=capture_dir)
		cv2.namedWindow('monitor',cv2.WINDOW_NORMAL)

	def process_monitor(self, img):
		counter=0
		cv2.putText(img, datetime.now().strftime('%H:%M:%S')+' F:'+str(counter), (10, 700), self.font, 1, (0, 255, 0), 2, cv2.LINE_AA)
		return img

	def monitor(self, img_monitor, img_processed, img):
		cv2.namedWindow('monitor',cv2.WINDOW_NORMAL)
		cv2.imshow("monitor", img_monitor)