__author__ = 'sami'

import os
import numpy

from libtiff import TIFF
from matplotlib import pyplot as plt

class Image(object):
    """
    A very simple class to contain image data 2D/3D
    """

    @classmethod
    def get_image_from_imagej_tiff(cls, path):

        assert os.path.isfile(path)
        assert path.endswith(('.tif', '.tiff'))

        image = TIFF.open(path)

        xresolution = float(image.GetField('XRESOLUTION'))
        yresolution = float(image.GetField('YRESOLUTION'))

        data = image.read_image()

        if data.shape[0] == 1:
            data = data[0]

        return cls(images=data, spacing=[1/xresolution, 1/yresolution])

    def __init__(self, images=None, spacing=None):

        self.images = numpy.array(images)
        self.spacing = list(spacing)

        assert len(spacing) == len(images.shape), (spacing, images.shape)

        self.data_type = self.images.dtype

    def __getitem__(self, *args):
        return self.images[args]

    def __mul__(self, other):
        if isinstance(other, Image):
            return Image(self.images * other.images, self.spacing)
        elif isinstance(other, (long, int, float, numpy.ndarray)):
            return Image(self.images * other, self.spacing)
        else:
            return None

    def get_spacing(self):
        return self.spacing

    def get_dimensions(self):
        return list(self.images.shape)

    def show(self):
        plt.imshow(self.images)
        plt.show()








