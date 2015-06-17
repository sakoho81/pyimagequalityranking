import sys
import os

from myimage import MyImage as Image
from filters import ImageResolution

path_prefix = "/home/sami/Pictures/Quality"

def main():
    if len(sys.argv) < 2:
        print "You must define a path to an image"
        sys.exit(1)

    path = sys.argv[1]

    real_path = os.path.join(path_prefix, path)
    image = Image.get_image_from_imagej_tiff(real_path)

    task = ImageResolution(image)
    task.calculate_power_spectrum(show=False)
    #task.calculate_radial_average(show=False)
    task.calculate_summed_power(show=True)
    #task.show_all()

if __name__ == "__main__":
    main()
