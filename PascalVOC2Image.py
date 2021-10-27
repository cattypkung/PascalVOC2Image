import numpy as np
import os
import pathlib
import shutil
import xml.etree.ElementTree as ET

from PIL import Image

# Set path directory
PATH_TO_CURRENT  = os.getcwd()
PATH_TO_LABELS   = os.path.join(PATH_TO_CURRENT, 'Labels', 'label_map.pbtxt')
PATH_TO_IMAGES   = pathlib.Path(os.path.join(PATH_TO_CURRENT,'ImagesXML'))
PATH_TO_COMPLETE = os.path.join(PATH_TO_IMAGES,'Complete')

#######################
#   FUNCTION DECLARE  #
#######################
def get_files(extensions):
    all_files = []
    for ext in extensions:
        all_files.extend(PATH_TO_IMAGES.glob(ext))
    return all_files

#######################
# PRE PROCESSING STEP #
#######################

# Create complete folder for moving original images
if not os.path.exists(PATH_TO_COMPLETE):
    os.makedirs(PATH_TO_COMPLETE)
    print("The Complete directory is created!")

#######################
#      EXECUTION      #
#######################
## Load images
IMAGE_LIST = get_files(('*.jpg', '*.png'))

for img in IMAGE_LIST:
    
    filename   = os.path.basename(img)
    _, fileext = os.path.splitext(filename)
    xml        = str(img)
    xml        = xml.replace(fileext,'.xml')
    destinationIMG = os.path.join(PATH_TO_COMPLETE,filename)
    destinationXML = destinationIMG.replace(fileext,'.xml')
    
    # XML Processing
    xml_tree   = ET.parse(xml)
    root       = xml_tree.getroot()

    # Load image
    print('Running PascalVOC for {}... '.format(filename), end='')
    image_np = np.array(Image.open(img).convert('RGB'))
    index = 0

    for name in root.iter('object'):
        class_name = name[0].text
        for box in name.iter('bndbox'):
            xmin = int(box[0].text)
            ymin = int(box[1].text)
            xmax = int(box[2].text)
            ymax = int(box[3].text)
            image_crop_array = image_np[ymin:ymax, xmin:xmax]
        
            # Convert array to image
            image_crop = Image.fromarray(image_crop_array)
            filename_temp = filename.replace(fileext, '_object_' + str(index) + '_' + class_name + fileext)
            filename_temp = os.path.join(PATH_TO_IMAGES, class_name, filename_temp)
            try:
                image_crop.save(filename_temp)
            except OSError:
                os.makedirs(os.path.join(PATH_TO_IMAGES,class_name))
                image_crop.save(filename_temp)
        
        index = index + 1
    
    # Move original image after finish finish
    shutil.move(img, destinationIMG)
    shutil.move(xml, destinationXML)
    
    print('done')