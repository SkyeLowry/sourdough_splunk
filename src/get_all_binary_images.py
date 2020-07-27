import sys
import os

from lib.SourDough import ImageFileUtil, ImageProcessor

if len(sys.argv) is 1:
    raise Exception('Please add a filename as an argument!')

# Image variables
ini_height_range = [0, 3000]
ini_width_range = [700, 1300]
width_increment = 100
left_edge = ini_width_range[0]

util = ImageFileUtil(
  current_py_dir=os.path.dirname(__file__),
  sys_argv=sys.argv[1],
  log_file_name='sourdough_results.log'
)

ip = ImageProcessor(imageFileUtil=util)

ip.get_all_threshold_images()
ip.get_a_threshold_image('threshold_li')
