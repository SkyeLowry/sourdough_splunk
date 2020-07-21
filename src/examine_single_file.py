import sys
import os

from dough.SourDough import ImageProcessor

import datetime as dtime
from datetime import datetime

import pytz
from tzlocal import get_localzone

if len(sys.argv) is 1:
  raise Exception('Please add a filename as an argument!')

# Directory variables
current_py_dir = os.path.dirname(__file__)
full_img_dir = os.path.join(current_py_dir, sys.argv[1])

if not os.path.isfile(full_img_dir):
  raise Exception(full_img_dir + ' does not exist!')

log_file_dir = os.path.join(current_py_dir, 'sourdough_results.log')

split_dir = full_img_dir.split('/')
img_dir = split_dir[len(split_dir) - 2]
img_file_name = split_dir[-1]

# Time variables
tz = get_localzone()
date, time, misc = img_file_name.split('_')
dt = dtime.datetime.strptime(date + time, '%Y-%m-%d%H-%M-%S')
local_dt = tz.localize(dt, is_dst=True)
utc_dt = local_dt.astimezone(pytz.utc)

# Image variables
ini_height_range = [0, 3000]
ini_width_range = [700, 1300]
width_increment = 100
left_edge = ini_width_range[0]


while True:
  ip = ImageProcessor(file_name=full_img_dir)

  width_slice = [left_edge, left_edge + width_increment]
  crop_area = ini_height_range + width_slice

  file_index, file_name, current_size, max_height = ip.analyze_image(crop_area=crop_area)

  left_edge = width_slice[1]

  if left_edge > ini_width_range[1]:
    print('Width out of range. Next..')
    break

  if current_size is not None:
    break

print('Dough height:', current_size, 'File: ', img_file_name)

log_values = (utc_dt, current_size, os.path.join(img_dir, file_name))
string_array = [str(x) for x in log_values]
joined_string = ','.join(string_array)

print('log file dir:', log_file_dir)

if os.path.isfile(log_file_dir):
  file = open(log_file_dir, 'a')

  file.write(joined_string + '\n')
  file.close()
else:
  with open(log_file_dir, 'w') as fp: 
    pass
