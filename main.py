from plugins.monitor import PluginMonitor
from plugins.timelapse import PluginTimelapse

import logging
import time
import cv2

CAMERA_INDEX = 1
CAMERA_HEIGHT = 1080
CAMERA_WIDTH = 1920

###### CONFIG ######

INTERVAL = 10

FILE_OUTPUT_DIR = "D:/StillsTEST/"
FILE_OUTPUT_FORMAT = "shot{:05d}.jpg"
FILE_OUTPUT_FORCED_FORMAT = "forced{:05d}.jpg"

PLUGINS = [
	PluginMonitor(),
	PluginTimelapse(FILE_OUTPUT_DIR, FILE_OUTPUT_FORMAT, INTERVAL),
]


###### Main ######
logging.basicConfig(level=logging.DEBUG, format='[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s')
log = logging.getLogger("Main")
log.info("Hellow world")

capture = cv2.VideoCapture(CAMERA_INDEX)
capture.set(3,CAMERA_WIDTH)
capture.set(4,CAMERA_HEIGHT)

#fourcc = cv2.cv.CV_FOURCC(*'XVID')  # cv2.VideoWriter_fourcc() does not exist
#video_writer = cv2.VideoWriter("output.avi", fourcc, 20, (680, 480))

log.info("Running pluging setups")
for plugin in PLUGINS:
	plugin.setup(PLUGINS, size=(CAMERA_WIDTH,CAMERA_HEIGHT),capture=capture, capture_dir=FILE_OUTPUT_DIR)

while True:
	ret,frame = capture.read()

	frame_processed = frame
	frame_monitor = cv2.resize(frame, (1280,720))

	for plugin in PLUGINS:
		if plugin.modify_original:
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