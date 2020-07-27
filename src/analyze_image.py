import sys
import os
from dotenv import load_dotenv
load_dotenv()

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

while True:
  ip = ImageProcessor(imageFileUtil=util)

  width_slice = [left_edge, left_edge + width_increment]

  crop_area = ini_height_range + width_slice

  file_name, current_size, max_height = ip.analyze_image(
    method_name=os.getenv('IMAGE_PROCESS_METHOD'),
    crop_area=crop_area
  )

  left_edge = width_slice[1]

  if left_edge > ini_width_range[1]:
    print('Width out of range. Next..')
    break

  if current_size is not None:
    break

print('Dough height:', current_size, 'File: ', util.img_file_name)

util.log_result((
  util.utc_dt_from_file_name,
  current_size,
  os.path.join(util.img_folder_dir, util.img_file_name)
))
