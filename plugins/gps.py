from . import Plugin, get_plugins_after_plugin, filecount_for_dir
from datetime import datetime
import cv2
import time
import socket
import io
import pynmea2
import math
import exif

class PluginGPS(Plugin):
	NAME = "GenericGPSPlugin"
	def __init__(self, name=NAME, reconnect_if_disconnect=True):
		Plugin.__init__(self,name=name)
		self.reconnect_if_disconnect= reconnect_if_disconnect
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

	@property
	def working(self):
		return self.sec_since_last_update < 5

	@staticmethod
	def deg_to_dms(deg, type='lat'):
		decimals, number = math.modf(deg)
		d = int(number)
		m = int(decimals * 60)
		s = (deg - d - m / 60) * 3600.00
		compass = {
			'lat': ('N','S'),
			'lon': ('E','W')
		}
		compass_str = compass[type][0 if d >= 0 else 1]
		return ((abs(d), abs(m), abs(s)), compass_str)

	def process_photo(self, file_path, image_description=None):
		with open(file_path, 'rb') as image_file:
			img = exif.Image(image_file)

		lat = PluginGPS.deg_to_dms(self._gps[0], type="lat")
		lon = PluginGPS.deg_to_dms(self._gps[1], type="lon")

		img.gps_latitude = lat[0]
		img.gps_latitude_ref = lat[1]
		img.gps_longitude = lon[0]
		img.gps_longitude_ref = lon[1]
		img.gps_altitude = self.altitude
		if image_description:
			img.image_description = image_description

		with open(file_path, 'wb') as updated_image_file:
		    updated_image_file.write(img.get_file())
		return True


class PluginGPS_TCP(PluginGPS):
	NAME = "NemaGPS_TCP"
	def __init__(self, ip_address, port, name=NAME, reconnect_if_disconnect=True):
		PluginGPS.__init__(self,name=name,reconnect_if_disconnect=reconnect_if_disconnect)
		self.ip_address = ip_address
		self.port = port
		self.sock = None
		self.sockfile = None
		self.recreate_socket()
		self.tlastsockupdate = 0

	def close_socket(self):
		if self.sock:
			self.sock.close()
		self.sock = None
		self.sockfile = None

	def recreate_socket(self):
		self.close_socket()
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		
	def setup(self, plugins=[], size=(0,0), capture=None, capture_dir=""):
		Plugin.setup(self, plugins=plugins, size=size, capture=capture, capture_dir=capture_dir)
		self.resetup_socket()

	def resetup_socket(self):
		try:
			self.sock.connect((self.ip_address, self.port))
			self.sock.setblocking(0)
			self.sockfile = self.sock.makefile()
			self.log.info("Socket reconnected")
		except ConnectionRefusedError as e:
			self.log.error(e)
		except TimeoutError as e:
			self.log.error(e)

	def process(self, _):
		if self.tlastsockupdate + 15 < time.time():
			try:
				self.sock.send(b"TEST")
			except Exception as e:
				self.log.error("Socket disconnected, reconnect enabled: %r" % (self.reconnect_if_disconnect))
				if self.reconnect_if_disconnect:
					self.log.info("Trying to reconnect")
					self.recreate_socket()
					self.resetup_socket()
					self.tlastsockupdate = time.time()
				else:
					self.tlastsockupdate = time.time() * 4 #Hacky way to diable the check

		if self.sockfile:
			try:
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
			except ConnectionResetError as e:
				self.close_socket()
				self.log.error("Socket disconnected: %r" % (e))
		return _

	def quit(self):
		self.close_socket()