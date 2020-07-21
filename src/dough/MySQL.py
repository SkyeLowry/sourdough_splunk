import re
import os
import datetime as dtime
from datetime import datetime

import pytz # $ pip install pytz
from tzlocal import get_localzone # $ pip install tzlocal

import sshtunnel
import mysql.connector
from mysql.connector import errorcode

from dotenv import load_dotenv
load_dotenv()

tz = get_localzone()

class MySQL():
  def __init__(self, port):
    print('port', port)
    try:
      cnx = mysql.connector.MySQLConnection(
        host=os.environ.get('MYSQL_HOST'),
        user=os.environ.get('MYSQL_USER'),
        passwd=os.environ.get('MYSQL_PASSWORD'),
        database=os.environ.get('MYSQL_DATABASE'),
        port=port
      )
    except mysql.connector.Error as err:
      if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        raise Exception("Something is wrong with your user name or password")
      elif err.errno == errorcode.ER_BAD_DB_ERROR:
        raise Exception("Database does not exist")
      else:
        raise Exception(err)
    else:
      self.cnx = cnx
      self.cursor = cnx.cursor()

  def close_connection(self):
    self.cnx.close()

  def get_image_group_id(self, group_name):
    select_id_query = 'SELECT id FROM ImageGroup WHERE name = "%s"' % (group_name)

    self.cursor.execute(select_id_query)
    id_response = self.cursor.fetchone()

    if id_response is None:
      self.create_image_group(group_name)
      group_id = self.get_image_group_id(group_name)

      print('Group ID: %d created!' % group_id)

      return group_id
    else:
      print('Group ID: %d' % id_response[0])

      return id_response[0]

  def create_image_group(self, group_name):
    try:
      query = 'INSERT INTO ImageGroup (`name`) VALUES ("%s")' % (group_name)
      self.cursor.execute(query)
      
      self.cnx.commit()
    except mysql.connector.errors.IntegrityError:
      print('create_image_group: Duplicate entry for ' + group_name + ' exists. Skipping...')

  def insert_image_analysis(
    self,
    group_id,
    file_index,
    img_file,
    current_size,
    max_height
  ):
    try:
      date, time, everything_else = img_file.split('_')
      utc_dt = self.__get_utc_time(date + time, '%Y-%m-%d%H-%M-%S', True).strftime('%Y-%m-%d %H:%M:%S')

      values = (group_id, file_index, '"' + img_file + '"', current_size or 'NULL', max_height, '"' + utc_dt + '"')
      query = 'INSERT INTO ImageAnalysis (`image_group_id`, `file_order`, `file_name`, `current_size`, `max_height`, `snap_date`) VALUES (%s, %s, %s, %s, %d,  %s)' % values

      self.cursor.execute(query)
      self.cnx.commit()

      self.cursor.execute('SELECT * FROM ImageAnalysis ORDER BY snap_date DESC LIMIT 1;')

      latest_record = self.cursor.fetchone()

      return latest_record
    except mysql.connector.errors.IntegrityError:
      print('insert_image_analysis: Duplicate entry for ' + img_file + ' exists. Skipping...')

  def __get_utc_time(self, str_datetime, format, is_dst):
    dt = dtime.datetime.strptime(str_datetime, format)
    local_dt = tz.localize(dt, is_dst=True)

    return local_dt.astimezone(pytz.utc)
