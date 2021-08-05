from plugins.monitor import PluginMonitor
from plugins.timelapse import PluginTimelapse
from plugins.manual_capture import PluginManualCapture
from plugins.video_recorder import PluginVideoCapture
from plugins.gps import PluginGPS_TCP

# from plugins.effects.roadmap import PluginEffectRoadmap

import logging
import time
import cv2
import numpy as np

###### CONFIG ######

CAMERA_INDEX = 1
CAMERA_HEIGHT = 1080
CAMERA_WIDTH = 1920
CAMERA_SETTINGS = [
	# (cv2.CAP_PROP_EXPOSURE, 1),
	# (cv2.CAP_PROP_WB_TEMPERATURE, 5700),
	# (cv2.CAP_PROP_BRIGHTNESS, 0),
	# (cv2.CAP_PROP_CONTRAST, 35),
	# (cv2.CAP_PROP_HUE, 5),
	# (cv2.CAP_PROP_SHARPNESS, 2.5),
	# (cv2.CAP_PROP_GAMMA, 110),
	# (cv2.CAP_PROP_GAIN, 0),
	# (cv2.CAP_PROP_AUTO_EXPOSURE, 0),
	# (cv2.CAP_PROP_AUTO_WB, 0),
]
INTERVAL = 10

FILE_OUTPUT_DIR = "D:/StillsTEST/"
FILE_OUTPUT_FORMAT = "shot{:05d}.jpg"
# FILE_OUTPUT_MAP_FORMAT = "mapshot{:05d}.jpg"
FILE_OUTPUT_FORCED_FORMAT = "forced{:05d}.jpg"
FILE_OUTPUT_VIDEO_FORMAT = "record{:05d}.avi"

PLUGINS = [
	PluginGPS_TCP("192.168.1.15", 6000),
	PluginTimelapse(FILE_OUTPUT_DIR, FILE_OUTPUT_FORMAT, INTERVAL),
	PluginManualCapture(FILE_OUTPUT_DIR, FILE_OUTPUT_FORCED_FORMAT, ord('s')),
	PluginVideoCapture(FILE_OUTPUT_DIR, FILE_OUTPUT_VIDEO_FORMAT, ord('r')),
	
	# PluginEffectRoadmap(
	# 	[(47.966671, 7.4), "Oberhergheim"],
	# 	[(43.2487, 3.2923), "Valras-Plage"],
	# 	7,
	# 	INTERVAL,
	# 	map_padding = [1,1,1,0],
	# 	map_crop=[175, 0],
	# ),
	PluginMonitor(),
	# PluginTimelapse(FILE_OUTPUT_DIR, FILE_OUTPUT_MAP_FORMAT, INTERVAL),
]


###### Main ######
logging.basicConfig(level=logging.DEBUG, format='[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s')
log = logging.getLogger("Main")
log.info("Hellow world")

capture = cv2.VideoCapture(CAMERA_INDEX)
capture.set(3,CAMERA_WIDTH)
capture.set(4,CAMERA_HEIGHT)

for prop, value in CAMERA_SETTINGS:
	capture.set(prop, value)

log.info("Running pluging setups")
for plugin in PLUGINS:
	plugin.setup(PLUGINS, size=(CAMERA_WIDTH,CAMERA_HEIGHT),capture=capture, capture_dir=FILE_OUTPUT_DIR)

while True:
	ret,frame = capture.read()

	frame_processed = frame
	frame_monitor = cv2.resize(frame, (1280,720))

	for plugin in PLUGINS:
		frame_processed = plugin.process(frame_processed)
		frame_monitor = plugin.process_monitor(frame_monitor)

	for plugin in PLUGINS:
		plugin.monitor(frame_monitor, frame_processed, frame)

	k = cv2.waitKey(1) & 0xFF
	for plugin in PLUGINS:
		plugin.onkeypress(k)

	for plugin in PLUGINS:
		plugin.write_file(frame_monitor, frame_processed, frame)
	
	if k == ord('q'):
		log.info("Q pressed, running plugins stop and exiting")
		for plugin in PLUGINS:
			plugin.quit()
		break

	# if cv2.waitKey(1) & 0xFF == ord('s'):
	# 	cv2.imwrite(FILE_OUTPUT_DIR + FILE_OUTPUT_FORCED_FORMAT.format(frame_counter_forced), frame)
	# 	print("Saved forced as: "+FILE_OUTPUT_DIR + FILE_OUTPUT_FORCED_FORMAT.format(frame_counter_forced))
	# 	frame_counter_forced += 1