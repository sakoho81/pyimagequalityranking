"""
File:        myimage.py
Author:      Sami Koho (sami.koho@gmail.com)

Description:
This file contains a simple class for storing image data.
There's really nothing groundbreaking here. An attempt was
made to create a simple class to contain only the
functionality required by the PyImageQualityRanking software.
"""

import os
import numpy
import scipy.ndimage.interpolation as itp
import argparse
from PIL import Image
from PIL.TiffImagePlugin import X_RESOLUTION, Y_RESOLUTION
from matplotlib import pyplot as plt
from math import log10, ceil, floor


def get_options(parser):
    """
    Command-line options for the image I/O
    """
    assert isinstance(parser, argparse.ArgumentParser)
    group = parser.add_argument_group("Image I/O", "Options for image file I/O")
    # Parameters for controlling how image files are handled
    group.add_argument(
        "--imagej",
        help="Defines wheter the image are in ImageJ tiff format, "
             "and thus contain the pixel size info etc in the TIFF tags. "
             "By default true",
        action="store_true"
    )
    group.add_argument(
        "--rgb-channel",
        help="Select which channel in an RGB image is to be used for quality"
             " analysis",
        dest="rgb_channel",
        type=int,
        choices=[0, 1, 2],
        default=1
    )
     # File filtering for batch mode processing
    parser.add_argument(
        "--average-filter",
        dest="average_filter",
        type=int,
        default=0,
        help="Analyze only images with similar amount of detail, by selecting a "
             "grayscale average pixel value threshold here"
    )
    parser.add_argument(
        "--file-filter",
        dest="file_filter",
        default=None,
        help="Define a common string in the files to be analysed"
    )
    return parser


class MyImage(object):
    """
    A very simple class to contain image data
    """

    @classmethod
    def get_image_from_imagej_tiff(cls, path):
        """
        A class method for opening a ImageJ tiff file. Using this method
        will enable the use of correct pixel size during analysis.
        :param path: Path to an image
        :return:     An object of the MyImage class
        """
        assert os.path.isfile(path)
        assert path.endswith(('.tif', '.tiff'))

        image = Image.open(path)

        xresolution = image.tag.tags[X_RESOLUTION][0][0]
        yresolution = image.tag.tags[Y_RESOLUTION][0][0]

        #data = utils.rescale_to_min_max(numpy.array(image), 0, 255)

        if data.shape[0] == 1:
            data = data[0]

        return cls(images=data, spacing=[1.0/xresolution, 1.0/yresolution])

    @classmethod
    def get_generic_image(cls, path):
        """
        A class method for opening all kinds of images. No attempt is made
        to read any tags, as most image formats do not have them. The idea
        was to keep this very simple and straightforward.
        :param path: Path to an image
        :return:     An object of the MyImage class
        """
        assert os.path.isfile(path)

        image = numpy.array(Image.open(path))
        #image = utils.rescale_to_min_max(image, 0, 255)

        return cls(images=image, spacing=[1, 1])


    def __init__(self, images=None, spacing=None):

        self.images = numpy.array(images)
        self.spacing = list(spacing)

        power = log10(spacing[0])
        if 3 < power <= 6:
            self.spacing_unit = 'um'
        elif 6 < power <= 9:
            self.spacing_unit = 'nm'
        else:
            self.spacing_unit = 'not_def'

        self.data_type = self.images.dtype

    def __getitem__(self, *args):
        return self.images[args]

    def __mul__(self, other):
        if isinstance(other, MyImage):
            return MyImage(self.images * other.images, self.spacing)
        elif isinstance(other, (long, int, float, numpy.ndarray)):
            return MyImage(self.images * other, self.spacing)
        else:
            return None

    def __sub__(self, other):
        assert isinstance(other, MyImage)
        assert other.get_dimensions() == self.get_dimensions()
        result = (self.images.astype(numpy.int16) - other.images).clip(0, 255).astype(numpy.uint8)
        return MyImage(result, self.spacing)

    def get_spacing(self):
        """
        Returns the pixel spacing information.
        """
        return self.spacing

    def get_dimensions(self):
        """
        Returns the image dimensions
        """
        return tuple(self.images.shape)

    def show(self):
        """
        Show a plot of the image
        """
        plt.imshow(self.images, cmap=plt.cm.binary)
        plt.show()

    def get_channel(self, channel):
        """
        Returns a new image containing a single color channel from
        a RGB image.
        """
        return MyImage(self.images[:, :, channel], self.spacing)

    def get_array(self):
        return self.images

    def get_min_and_max(self):
        return self.images.min(), self.images.max()

    def is_rgb(self):
        """
        Check if the image is an RGB image.
        """

        if len(self.images.shape) == 3:
            return True
        else:
            return False

    def save(self, filename):
        """
        Saves the image using PIL image.save() routine
        """
        image = Image.fromarray(numpy.uint8(self.images))
        image.save(filename)

    def average(self):
        """
        :return: Average grayscale pixel value of the image
        """
        return numpy.mean(self.images)

    def crop_to_rectangle(self):
        """
        Crop the image into a square. This is sometimes useful, especially
        in methods employing FFT.
        """
        dims = self.images.shape

        if dims[0] > dims[1]:
            diff = 0.5*(dims[0]-dims[1])
            self.images = self.images[int(floor(diff)): -int(ceil(diff)), :]
        elif dims[1] > dims[0]:
            diff = 0.5*(dims[1]-dims[0])
            self.images = self.images[:, int(floor(diff)): -int(ceil(diff))]

    def resize(self, size):
        """
        Resize the image, using cubic interpolation.

        :param size: A tuple of new image dimensions.

        """
        assert isinstance(size, tuple)
        zoom = [float(a)/b for a, b in zip(size, self.images.shape)]
        print("The zoom is %s" % zoom)

        self.images = itp.zoom(self.images, tuple(zoom), order=3)








