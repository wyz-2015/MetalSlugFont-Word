import os
import glob
def remove_images(directory_path):
    files = glob.glob(os.path.join(directory_path, '*'))
    [os.remove(file) for file in files if os.path.isfile(file)]
image_directory = "src/static/generated-images/"
remove_images(image_directory)