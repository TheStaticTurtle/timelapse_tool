from .. import Plugin, get_plugins_after_plugin, filecount_for_dir
from datetime import datetime
import cv2
import time
from pathlib import Path
import numpy as np
import math
from PIL import Image, ImageDraw, ImageFont
import io,requests
import os

TILE_SIZE = 256

def deg2num(lat_deg, lon_deg, zoom):
	lat_rad = math.radians(lat_deg)
	n = 2.0 ** zoom
	xtile = int((lon_deg + 180.0) / 360.0 * n)
	ytile = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
	return (xtile, ytile)

def deg2tile_pixel_marker(lat_deg, lon_deg, zoom):
	lat_rad = math.radians(lat_deg)
	n = 2.0 ** zoom
	xtile = ((lon_deg + 180.0) / 360.0 * n)
	ytile = ((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
	return (xtile%1 * TILE_SIZE, ytile%1 * TILE_SIZE)

def get_map_at_pos(cx,cy,zoom):
	r = requests.get("https://a.tile.openstreetmap.org/%d/%d/%d.png" % (zoom,cx,cy))
	if r.status_code != requests.codes.ok:
		assert False, 'Status code error: {}.'.format(r.status_code)
	return Image.open(io.BytesIO(r.content))

def tiles_for_path(zoom, gps_1, gps_2, ptop=0, pbot=0, pleft=0, pright=0):
	c1_x, c1_y = deg2num(gps_1[0], gps_1[1], zoom)
	c2_x, c2_y = deg2num(gps_2[0], gps_2[1], zoom)
	img1 = get_map_at_pos(c1_x, c1_y, zoom)
	img2 = get_map_at_pos(c2_x, c2_y, zoom)

	y_diff = abs(c1_y - c2_y)
	x_diff = abs(c1_x - c2_x)
	min_x = min(c1_x, c2_x)
	min_y = min(c1_y, c2_y)

	dst = Image.new('RGB', (TILE_SIZE*(x_diff+1+pleft+pright), TILE_SIZE*(y_diff+1+ptop+pbot)))

	array = [ [None]*(y_diff+1+ptop+pbot) for i in range(x_diff+1+pleft+pright)]

	array[c1_x - min_x + pleft][c1_y - min_y + ptop] = img1
	array[c2_x - min_x + pleft][c2_y - min_y + ptop] = img2

	for x,col in enumerate(array):
		for y,img in enumerate(col):
			if img is None:
				array[x][y] = get_map_at_pos(x + min_x - pleft, y + min_y - ptop, zoom)

	for x,col in enumerate(array):
		for y,img in enumerate(col):
			if img:
				dst.paste(img, (x*TILE_SIZE, y*TILE_SIZE))

	return dst, min_x, min_y

def draw_maker_at_pos(img, gps, zoom, min_x, min_y, name, icon_file, icon_size, ptop=0, pleft=0):
	c_x, c_y = deg2num(gps[0], gps[1], zoom)
	mr_x, mr_y = deg2tile_pixel_marker(gps[0], gps[1], zoom)
	m_x = (c_x - min_x + pleft)* TILE_SIZE + mr_x 
	m_y = (c_y - min_y + ptop)* TILE_SIZE + mr_y 
	
	icon_img = Image.open(icon_file)
	icon_img.thumbnail((icon_img.width * (icon_size/100), icon_img.height * (icon_size/100)), Image.ANTIALIAS)

	i_x = int(m_x - icon_img.width / 2)
	i_y = int(m_y - icon_img.height)
	img.paste(icon_img, (i_x, i_y), icon_img)

	font = ImageFont.truetype("arial", size=25)
	name_w, name_h = font.getsize(name)

	t_x = int(m_x - name_w / 2)
	t_y = int(m_y - icon_img.height - name_h *1.25)

	draw = ImageDraw.Draw(img, "RGB")
	draw.rectangle(((t_x -10 , t_y - 5), (t_x+name_w+10, t_y+name_h+5)), fill=(0,0,0))
	draw.text((t_x, t_y), name, font=font)

	return img

def draw_path(img, gps_points, zoom, min_x, min_y, ptop=0, pleft=0):
	draw = ImageDraw.Draw(img)

	if len(gps_points) >= 2:
		for i, point in enumerate(gps_points):
			if i==0:
				continue
			last_point = gps_points[i-1]
			
			c1_x, c1_y = deg2num(point[0], point[1], zoom)
			p1r_x, p1r_y = deg2tile_pixel_marker(point[0], point[1], zoom)
			p1_x = (c1_x - min_x + pleft)* TILE_SIZE + p1r_x 
			p1_y = (c1_y - min_y + ptop)* TILE_SIZE + p1r_y 

			c2_x, c2_y = deg2num(last_point[0], last_point[1], zoom)
			p2r_x, p2r_y = deg2tile_pixel_marker(last_point[0], last_point[1], zoom)
			p2_x = (c2_x - min_x + pleft)* TILE_SIZE + p2r_x 
			p2_y = (c2_y - min_y + ptop)* TILE_SIZE + p2r_y 
	

			draw.line((p1_x, p1_y, p2_x, p2_y), fill=(255,0,255), width=4)

	return img

# def get_map(start_gps, start_name, end_gps, end_name, zoom=7, map_padding=[0,0,0,0]):
# 	fdir = os.path.dirname(__file__)
# 	m, min_x, min_y = tiles_for_path(zoom, start_gps, end_gps, ptop=map_padding[0], pbot=map_padding[1], pleft=map_padding[2], pright=map_padding[3])
# 	m = draw_maker_at_pos(m, start_gps, zoom, min_x, min_y, start_name, fdir+"/map/icon_start.png", 50, ptop=map_padding[0], pleft=map_padding[2])
# 	m = draw_maker_at_pos(m, end_gps, zoom, min_x, min_y, end_name, fdir+"/map/icon_end.png", 50, ptop=map_padding[0], pleft=map_padding[2])
# 	m = draw_path(m, [
# 		start_gps,
# 		end_gps
# 	], zoom, min_x, min_y, ptop=map_padding[0], pleft=map_padding[2])
# 	m.show()



class PluginEffectRoadmap(Plugin):
	NAME = "EffectRoadmap"
	def __init__(self, start_gps, end_gps, zoom, interval, map_padding=[0,0,0,0], map_crop=[0,0], name=NAME):
		Plugin.__init__(self,name=name)
		fdir = os.path.dirname(__file__)
		self.map_padding = map_padding
		self.zoom = zoom
		self.start_gps = start_gps
		self.end_gps = end_gps
		self.mapcrop_left = map_crop[0] 
		self.mapcrop_right = map_crop[1]
		self.interval = interval
		
		self.map, self.min_x, self.min_y = tiles_for_path(self.zoom, self.start_gps[0], self.end_gps[0], ptop=self.map_padding[0], pbot=self.map_padding[1], pleft=self.map_padding[2], pright=self.map_padding[3])
		self.map = draw_maker_at_pos(self.map, self.start_gps[0], self.zoom, self.min_x, self.min_y, self.start_gps[1], fdir+"/map/icon_start.png", 50, ptop=self.map_padding[0], pleft=self.map_padding[2])
		self.map = draw_maker_at_pos(self.map, self.end_gps[0], self.zoom, self.min_x, self.min_y, self.end_gps[1], fdir+"/map/icon_end.png", 50, ptop=self.map_padding[0], pleft=self.map_padding[2])
		# self.map.show()
		self.tlast = 0
		self.visited_gps = []	

	def setup(self, plugins=[], size=(0,0), capture=None, capture_dir=""):
		Plugin.setup(self, plugins=plugins, size=size, capture=capture, capture_dir=capture_dir)

	def process(self, img):
		return self.process_monitor(img)

	def process_monitor(self, img):
		if time.time() > (self.tlast + self.interval):
			for plugin in self.plugins:
				if plugin.gps:
					self.visited_gps.append(plugin.gps)
					break
			tlast = time.time()

		map_with_path = draw_path(self.map, self.visited_gps, self.zoom, self.min_x, self.min_y, ptop=self.map_padding[0], pleft=self.map_padding[2])
		
		map_height, map_width = map_with_path.height, map_with_path.width
		img_height, img_width, _ = img.shape
		
		new_map_width = int(map_width * img_height / map_height)

		cv_map = np.array(map_with_path)
		cv_map = cv2.cvtColor(cv_map, cv2.COLOR_BGR2RGB)

		cv_map = cv2.resize(cv_map, (new_map_width, img_height), interpolation = cv2.INTER_CUBIC)

		w = new_map_width - self.mapcrop_right
		cv_map = cv_map[0:0+img_height, self.mapcrop_left:self.mapcrop_left+w]

		y_offset = 0
		x_offset = img_width-new_map_width + self.mapcrop_left

		img[y_offset:y_offset+cv_map.shape[0], x_offset:x_offset+cv_map.shape[1]] = cv_map
		return img

# get_map((47.966671, 7.4), "Oberhergheim", (43.2487, 3.2923), "Valras-plage", zoom=7, map_padding=[0,0,0,0])
# get_map((43.2487, 3.2923), "Valras-Plage", (47.966671, 7.4), "Oberhergheim", zoom=7, map_padding=[0,0,1,0])
