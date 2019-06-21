#!/usr/bin/env python
# -*- python -*-

"""
File: test_resolution_filter.py
Author: Sami Koho

Description:
A utility for testing the Frequency domain filter. Produces
plots of 2D and 1D power spectra of an image. The image file
can be specified with command line parameters --file and
--working-directory.
"""
import sys
import os

from myimage import MyImage as Image
from pyimq import script_options
from pyimq.filters import FrequencyQuality


def main():

    options = script_options.get_quality_script_options(sys.argv[1:])
    path = options.working_directory
    filename = options.file

    if os.path.isfile(filename):
        real_path = filename
    elif os.path.isfile(os.path.join(path, filename)):
        real_path = os.path.join(path, filename)
    else:
        print("Not a valid file!")
        sys.exit()

    image = Image.get_image_from_imagej_tiff(real_path)

    task = FrequencyQuality(image, options)
    task.calculate_power_spectrum()
    task.calculate_summed_power()

if __name__ == "__main__":
    main()
