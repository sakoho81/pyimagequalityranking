__author__ = 'sami'

import os
import numpy

from libtiff import TIFF3D


class Image(object):
    """
    A very simple class to contain image data 2D/3D
    """

    @classmethod
    def get_image_from_imagej_tiff(cls, path):

        assert os.path.isfile(path)
        assert path.endswith(('.tif', '.tiff'))

        image = TIFF3D.open(path)

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

    def get_spacing(self):
        return self.spacing

    def get_dimensions(self):
        return list(self.images.shape)






