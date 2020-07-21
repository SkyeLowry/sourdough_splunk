import re

from skimage import io
from skimage.filters import threshold_li, try_all_threshold
from skimage.measure import label, regionprops

import matplotlib.pyplot as plt

class ImageProcessor():
  def __init__(self, file_name):
    self.file_name = file_name
    self.file_index = self.__get_file_index()
    self.img = io.imread(self.file_name, as_gray=True)
    self.default_crop_area = [0, 3000, 500, 1200]
    self.default_min_area = 20000
    self.height = None
    
    # Region analysis results when area is > min_area
    self.bounds = [] 
    
  def __get_file_index(self):
    index_reg = re.match(r".*\((\d+)\)\.jpg$", self.file_name)

    return index_reg.group(1)

  def load_image(self, crop_area=None, download_img=False):
    if crop_area is None:
      crop_area = self.default_crop_area 
      
    # crop image to zoom in to jar
    img_cropped = self.__crop_image(crop_area)   
    binary_img = self.__get_binary_image(img_cropped)

    if download_img:
      # All binary image set
      fig_all, ax_all = try_all_threshold(self.img, figsize=(10, 8), verbose=False)
      plt.savefig('all_binary_images.png')
      print('all_binary_images.png generated!')

      fig, ax = plt.subplots(ncols=2)
      # Cropped image
      ax[0].imshow(img_cropped, cmap=plt.cm.gray)
      ax[0].set_title('Cropped Image')

      # Li filtered image
      ax[1].imshow(binary_img, cmap=plt.cm.gray)
      ax[1].set_title('Binary Image by Li Filter')

      plt.savefig('image_analysis.png')
      print('image_analysis.png generated!')

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
    ax.imshow(binary_img, cmap=plt.cm.gray)

    for bound in self.bounds:
      y0, x0 = bound['centroid']
      
      # Plot the bounding box
      ax.plot(bound['box_bx'], bound['box_by'], '-b', linewidth=2)

      # Plot the centroid
      ax.plot(x0, y0, 'ro')

    ax.set_title('Dough Area')

    return plt
    
  def analyze_image(self, crop_area=None, min_area=None):
    if crop_area is None:
      crop_area = self.default_crop_area
    
    if min_area is None:
      min_area = self.default_min_area
    
    # crop image to zoom in to jar
    img_cropped = self.__crop_image(crop_area)   
    binary_img = self.__get_binary_image(img_cropped)

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

    return (self.file_index, self.file_name.split('/')[-1], current_size, max_height)

  def __crop_image(self, crop_area):
    try:
      return self.img[crop_area[0]:crop_area[1], crop_area[2]:crop_area[3]]
    except ValueError:
      print('---')

  def __get_binary_image(self, image):
    thresh = threshold_li(image)

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
