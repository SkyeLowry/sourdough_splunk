import re
import os

import datetime as dtime
from datetime import datetime

import pytz
from tzlocal import get_localzone

from skimage import io, filters, measure
from skimage.measure import label, regionprops

import matplotlib.pyplot as plt

class ImageFileUtil():
  def __init__(self, current_py_dir, sys_argv, log_file_name):
    self.current_py_dir = current_py_dir
    self.sys_argv = sys_argv
    self.log_file_name = log_file_name

    if not os.path.isfile(self.full_img_file_name):
      raise Exception(self.full_img_file_name + ' does not exist!')

    if not os.path.isfile(self.full__log_file_name):
      with open(self.full__log_file_name, 'w') as fp:
        pass

  @property
  def img_folder_dir(self):
    split_dir = self.full_img_file_name.split('/')
    return split_dir[len(split_dir) - 2]
  
  @property
  def img_file_name(self):
    split_dir = self.full_img_file_name.split('/')
    return split_dir[-1]

  @property
  def full_img_file_name(self):
    return os.path.join(self.current_py_dir, self.sys_argv)
  
  @property
  def full__log_file_name(self):
    return os.path.join(self.current_py_dir, self.log_file_name)

  @property
  def utc_dt_from_file_name(self):
    tz = get_localzone()

    date, time, misc = self.img_file_name.split('_')

    dt = dtime.datetime.strptime(date + time, '%Y-%m-%d%H-%M-%S')

    local_dt = tz.localize(dt, is_dst=True)

    return local_dt.astimezone(pytz.utc)

  def log_result(self, log_array):
    string_array = [str(x) for x in log_array]

    joined_string = ','.join(string_array)

    if os.path.isfile(self.full__log_file_name):
      file = open(self.full__log_file_name, 'a')

      file.write(joined_string + '\n')

      file.close()
    else:
      with open(self.full__log_file_name, 'w') as fp:
        pass


class ImageProcessor(ImageFileUtil):
  def __init__(self, imageFileUtil):
    super().__init__(
      current_py_dir=imageFileUtil.current_py_dir,
      sys_argv=imageFileUtil.sys_argv,
      log_file_name=imageFileUtil.log_file_name
    )

    self.img = io.imread(self.full_img_file_name, as_gray=True)
    self.default_crop_area = [0, 3000, 500, 1200]
    self.default_min_area = 20000
    self.height = None
    
    # Region analysis results when area is > min_area
    self.bounds = [] 

  def get_all_threshold_images(self):
    # All binary image set
    fig_all, ax_all = filters.try_all_threshold(self.img, figsize=(10, 8), verbose=False)

    plt.savefig('imgs/all_binary_images.png')

    print('all_binary_images.png saved in imgs folder')

  def get_a_threshold_image(self, method_name, crop_area=None):
    if crop_area is None:
      crop_area = self.default_crop_area 
      
    # crop image to zoom in to jar
    img_cropped = self.__crop_image(crop_area)   
    binary_img = self.__get_binary_image(
      image=img_cropped, 
      method_name=method_name
    )

    fig, ax = plt.subplots(ncols=2)

    # Cropped image
    ax[0].imshow(img_cropped, cmap='gray')
    ax[0].set_title('Cropped Image')

    # Filtered image
    ax[1].imshow(binary_img, cmap='gray')
    ax[1].set_title('Binary Image by %s filter' % method_name)

    plt.savefig('imgs/binary_image_by_%s.png' % method_name)
    print('imgs/binary_image_by_%s.png saved in imgs folder' % method_name)

    return binary_img

  def get_height(self, binary_img, min_area=None, download_img=False):
    if min_area is None:
      min_area = self.default_min_area

    regions = self.__get_image_regions(binary_img)

    for region in regions:
      self.__set_bounds(region, min_area, binary_img)

    if download_img:
      graph = self.get_height_graph(binary_img)
      graph.savefig('height_analysis.png')
      
    return self.height

  def get_height_graph(self, binary_img):
    fix, ax = plt.subplots()
    ax.imshow(binary_img, cmap='gray')

    for bound in self.bounds:
      y0, x0 = bound['centroid']
      
      # Plot the bounding box
      ax.plot(bound['box_bx'], bound['box_by'], '-b', linewidth=2)

      # Plot the centroid
      ax.plot(x0, y0, 'ro')

    ax.set_title('Dough Area')

    return plt
    
  def analyze_image(self, method_name, crop_area=None, min_area=None):
    if crop_area is None:
      crop_area = self.default_crop_area
    
    if min_area is None:
      min_area = self.default_min_area
    
    # crop image to zoom in to jar
    img_cropped = self.__crop_image(crop_area)   
    binary_img = self.__get_binary_image(image=img_cropped, method_name=method_name)

    height = self.get_height(binary_img)
    max_height, max_width = binary_img.shape

    if max_height is None or height is None:
      current_size = None
    elif height == 0:
      current_size = None
    elif max_height == height:
      current_size = None
    else:
      current_size = abs(max_height - height)

    return (self.img_file_name, current_size, max_height)

  def __crop_image(self, crop_area):
    try:
      return self.img[crop_area[0]:crop_area[1], crop_area[2]:crop_area[3]]
    except ValueError:
      print('---')

  def __get_binary_image(self, image, method_name):
    allowed_methods=[
      'threshold_otsu',
      'threshold_yen',
      'threshold_isodata',
      'threshold_li',
      'threshold_local',
      'threshold_minimum',
      'threshold_mean',
      'threshold_niblack',
      'threshold_sauvola',
      'threshold_triangle',
      'threshold_multiotsu',
    ]

    if method_name not in allowed_methods:
      raise ValueError('Invalid method name, Expected one of: %s' % allowed_methods)
    
    threshold_method = getattr(filters, method_name)

    thresh = threshold_method(image)

    return image < thresh

  def __get_image_regions(self, binary_img):
    label_img = label(binary_img)
    regions = regionprops(label_img)  

    return regions 

  def __set_bounds(self, region, min_area, binary_img):
    max_height, max_width = binary_img.shape

    y0, x0 = region.centroid
    ymin, xmin, ymax, xmax = region.bbox

    # bx and by pairs are coordinates of a box clock-wise 
    # starting from top-left corner
    bx = (xmin, xmax, xmax, xmin, xmin)
    by = (ymin, ymin, ymax, ymax, ymin)

    area = (xmax - xmin) * (ymax - ymin)

    # We only want to take a box at the bottom of the image
    threshold_perc = 0.1
    is_bottom_box = (max_height * (1 - threshold_perc)) <= ymax and ymax <= (max_height * (1 + threshold_perc)) 

    if area > min_area and is_bottom_box and ymin is not 0:
      self.bounds.append({
        'centroid': (y0, x0),
        'box': (ymin, xmin, ymax, xmax),
        'box_bx': bx,
        'box_by': by
      })

      self.height = ymin
