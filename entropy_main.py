import sys
from image import Image

import os
import csv

from filters import LocalImageQuality

path_prefix = "/Users/sami/Documents"


def main():
    if len(sys.argv) < 3:
        print "Usage: python entropy_main.py [-mode] path"
        print "In which mode can be either file (f) or directory (d)"
        sys.exit(1)

    mode = sys.argv[1]
    path = sys.argv[2]

    if '-f' in mode:
        real_path = os.path.join(path_prefix, path)
        image = Image.get_image_from_imagej_tiff(real_path)

        task = LocalImageQuality(image)
        task.set_smoothing_kernel_size(100)
        entropy = task.calculate_image_quality()

        print "The entropy value of %s is %f" % (path, entropy)

    elif '-d' in mode:
        assert os.path.isdir(path), path

        output_file = open(os.path.join(path, "image_quality_results.csv", 'wt'))
        output_writer = csv.writer(output_file, quoting=csv.QUOTE_NONNUMERIC)
        output_writer.writerow(("Filename", "Entropy"))

        for filename in os.listdir(path):
            if filename.endswith(('.tif', '.tiff')):
                real_path = os.path.join(path, filename)
                image = Image.get_image_from_imagej_tiff(real_path)

                task = LocalImageQuality(image)
                task.set_smoothing_kernel_size(100)
                entropy = task.calculate_image_quality()

                print "The entropy value of %s is %f" % (filename, entropy)
                output_writer.writerow((filename, entropy))

        output_file.close()

    else:
        print "Unknown mode parameter %s. Please choose either -f or -d" % mode


if __name__ == "__main__":
    main()