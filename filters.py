import numpy
from scipy import ndimage

from image import Image


class Filter(object):
    """
    A base class for a filter utilizing Image class object
    """
    def __init__(self, image, physical=False):

        assert isinstance(image, Image)

        self.data = image

        self.spacing = self.data.get_spacing()
        self.dimensions = self.data.get_dimensions()
        self.physical = physical

    def set_physical_coordinates(self):
        self.physical = True

    def set_pixel_coordinates(self):
        self.physical = False


class LocalImageQuality(Filter):
    """
    Quantification of image quality is based on local sampling of image
    entropy. The samples are usually drawn from areas of highest amount
    of details
    """

    def __init__(self, image, physical=False):

        Filter.__init__(self, image, physical)

        self.data_temp = None
        self.kernel_size = []

    def set_smoothing_kernel_size(self, size):

        if isinstance(size, list):
            assert len(size) == len(self.spacing)
            sizes = size
        elif isinstance(size, float) or isinstance(size, int):
            sizes = []
            for i in self.spacing:
                sizes.append(size)
        else:
            print "Unknown size type"
            return

        if self.physical is True:
            for i in range(len(sizes)):
                self.kernel_size[i] = sizes[i]/self.spacing[i]
                assert self.kernel_size[i] < self.dimensions[i]
        else:
            self.kernel_size = sizes
            assert self.kernel_size < self.dimensions, \
                "Kernel can not be larger than image"

    def run_mean_smoothing(self, return_result=False):

        assert len(self.kernel_size) == len(self.dimensions)
        self.data_temp = ndimage.uniform_filter(self.data[:], size=self.kernel_size)

        if return_result:
            return Image(self.data_temp, self.spacing)

    def run_gaussian_smoothing(self, return_result=False):
        self.data_temp = ndimage.gaussian_filter(self.data[:], size=self.kernel_size)

        if return_result:
            return self.data_temp

    def calculate_entropy(self):
        # Calculate histogram
        histogram = ndimage.histogram(
            self.data_temp,
            self.data_temp.min(),
            self.data_temp.max(), 100)[1:]
        # Exclude zeros
        histogram = histogram[histogram > 0]
        # Normalize histogram bins to sum to one
        histogram = histogram.astype(float)/histogram.sum()

        return -numpy.sum(histogram*numpy.log2(histogram))

    def find_sampling_positions(self):
        peaks = numpy.percentile(self.data_temp, 85)
        return numpy.where(self.data_temp >= peaks, 1, 0)

    def calculate_image_quality(self, kernel=None):
        if kernel is not None:
            self.set_smoothing_kernel_size(kernel)

        assert len(self.kernel_size) != 0

        if self.data_temp is None:
            self.run_mean_smoothing()

        positions = self.find_sampling_positions()
        self.data_temp = self.data[:]*positions

        Image(self.data_temp, self.spacing).show()

        return self.calculate_entropy()













