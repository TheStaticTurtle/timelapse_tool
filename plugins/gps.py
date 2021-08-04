from . import Plugin, get_plugins_after_plugin, filecount_for_dir
from datetime import datetime
import cv2
import time
import socket
import io
import pynmea2

class PluginGPS(Plugin):
	NAME = "GenericGPSPlugin"
	def __init__(self, name=NAME):
		Plugin.__init__(self,name=name)
		self._altitude = 0
		self._gps = (0, 0)
		self._last_update = 0

	@property
	def altitude(self):
		return self._altitude

	@property
	def gps(self):
		return self._gps

	@property
	def sec_since_last_update(self):
		return time.time() - self._last_update
	
class PluginGPS_TCP(PluginGPS):
	NAME = "NemaGPS_TCP"
	def __init__(self, ip_address, port, name=NAME):
		PluginGPS.__init__(self,name=name)
		self.ip_address = ip_address
		self.port = port
		self.sock = None
		self.sockfile = None
		self.recreate_socket()
		self.tlastsockupdate = 0

	def recreate_socket(self):
		if self.sock:
			self.sock.close()
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sockfile = None

	def setup(self, plugins=[], size=(0,0), capture=None, capture_dir=""):
		Plugin.setup(self, plugins=plugins, size=size, capture=capture, capture_dir=capture_dir)
		self.resetup_socket()

	def resetup_socket(self):
		try:
			self.sock.connect((self.ip_address, self.port))
			self.sock.setblocking(0)
			self.sockfile = self.sock.makefile()
		except ConnectionRefusedError as e:
			print(e)

	def process(self, _):
		if self.tlastsockupdate + 15 < time.time():
			try:
				self.sock.send(b"TEST")
			except Exception as e:
				self.recreate_socket()
				self.resetup_socket()
				self.tlastsockupdate = time.time()
			
		if self.sockfile:
			line = self.sockfile.readline()
			if line:
				try:
					msg = pynmea2.parse(line)
					# self.log.debug("%r"%msg)
					if "GGA" in str(type(msg)):
						self._gps = (msg.latitude, msg.longitude)
						self._last_update = time.time()
						self._altitude = msg.altitude
						self.log.info("GPS Update: latitude=%f longitude=%f" % (msg.latitude, msg.longitude))
				except pynmea2.nmea.SentenceTypeError as e:
					pass
				except pynmea2.nmea.ParseError as e:
					pass
		return _

	def quit(self):
		self.sock.close()