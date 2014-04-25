import sys
from image import Image, Filter

import os
import numpy

from scipy import ndimage, stats

from libtiff import TIFF, TIFFfile


def main():
    if len(sys.argv) < 3:
        print "Usage: python entropy_main.py [-mode] path" \
              "In which mode can be either file (f) or directory" \
              "(d)"
        sys.exit(1)

    mode = sys.argv[1]
    path = sys.argv[2]

    if '-f' in mode:
        image = Image.get_image_from_imagej_tiff(path)
        print image.get_spacing()
        filter = Filter(image)







if __name__ == "__main__":
    main()