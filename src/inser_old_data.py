import sys
import os

import sshtunnel
import mysql.connector
from mysql.connector import errorcode

import glob
from dough.SourDough import ImageProcessor
from dough.MySQL import MySQL

from dotenv import load_dotenv
load_dotenv()

if len(sys.argv) is 1:
  raise Exception('Please add a filename as an argument!')

# Directory variables
current_py_dir = os.path.dirname(__file__)
full_img_dir = os.path.join(current_py_dir, sys.argv[1])

ini_height_range = [0, 3000]
ini_width_range = [700, 1100]
width_increment = 100

if not os.path.isdir(full_img_dir):
  raise Exception(full_img_dir + ' does not exist!')

with sshtunnel.SSHTunnelForwarder(
  ssh_address_or_host=os.environ.get('SSH_HOST'),
  ssh_username=os.environ.get('SSH_USER'),
  ssh_pkey=os.path.join(os.path.expanduser('~'), os.environ.get('SSH_KEY_DIR')),
  remote_bind_address=(os.environ.get('MYSQL_HOST'), os.environ.get('MYSQL_PORT'))
) as tunnel:
  mysql = MySQL(port=tunnel.local_bind_port)

  full_full_img_dir = os.path.join(full_img_dir, '*.jpg')
  folder_name = sys.argv[1].split('/')[-1]

  img_files = glob.glob(full_full_img_dir)
  img_files = sorted(img_files)

  group_id = mysql.get_image_group_id(folder_name)

  for i, img_name in enumerate(img_files):
    left_edge = ini_width_range[0]

    while True:
      ip = ImageProcessor(file_name=img_name)

      width_slice = [left_edge, left_edge + width_increment]
      crop_area = ini_height_range + width_slice

      file_index, file_name, current_size, max_height = ip.analyze_image(crop_area=crop_area)

      left_edge = width_slice[1]
      
      if left_edge > ini_width_range[1]:
        print('Width out of range. Next..')
        break

      if current_size is not None:
        break
      
    img_file = file_name.split('/')[-1]

    print('Dough height:', current_size, 'File: ', img_file)

    mysql.insert_image_analysis(group_id, file_index, img_file, current_size, max_height)

  mysql.close_connection()
