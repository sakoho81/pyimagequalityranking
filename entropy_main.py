import sys
from image import Image

import os

from filters import LocalImageQuality

path_prefix = "/Users/sami/Documents"

def main():
    if len(sys.argv) < 3:
        print "Usage: python entropy_main.py [-mode] path"
        print "In which mode can be either file (f) or directory (d)"
        sys.exit(1)

    mode = sys.argv[1]
    path = sys.argv[2]
    image = None

    if '-f' in mode:
        real_path = os.path.join(path_prefix, path)
        image = Image.get_image_from_imagej_tiff(real_path)

    task = LocalImageQuality(image)
    task.set_smoothing_kernel_size(100)
    result = task.run_mean_smoothing(return_result=True)

    mask = Image(task.find_sampling_positions(), image.get_spacing())

    result = mask*image

    result.show()

if __name__ == "__main__":
    main()