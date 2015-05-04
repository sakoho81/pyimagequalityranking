__author__ = 'sami'

import os
import numpy

from PIL import Image
from PIL.TiffImagePlugin import X_RESOLUTION, Y_RESOLUTION
from matplotlib import pyplot as plt
from math import log10

import utils


class MyImage(object):
    """
    A very simple class to contain image data 2D/3D
    """

    @classmethod
    def get_image_from_imagej_tiff(cls, path):

        assert os.path.isfile(path)
        assert path.endswith(('.tif', '.tiff'))

        image = Image.open(path)

        xresolution = image.tag.tags[X_RESOLUTION][0][0]
        yresolution = image.tag.tags[Y_RESOLUTION][0][0]

        data = utils.rescale_to_min_max(numpy.array(image), 0, 255)

        if data.shape[0] == 1:
            data = data[0]

        return cls(images=data, spacing=[1.0/xresolution, 1.0/yresolution])

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

        assert len(spacing) == len(images.shape), (spacing, images.shape)

        self.data_type = self.images.dtype

    def __getitem__(self, *args):
        return self.images[args]

    def __mul__(self, other):
        if isinstance(other, Image):
            return MyImage(self.images * other.images, self.spacing)
        elif isinstance(other, (long, int, float, numpy.ndarray)):
            return MyImage(self.images * other, self.spacing)
        else:
            return None

    def get_spacing(self):
        return self.spacing

    def get_dimensions(self):
        return list(self.images.shape)

    def show(self):
        plt.imshow(self.images)
        plt.show()








