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

        Filter.__init__(image, physical)

        self.data_temp = None
        self.kernel_size = []
        self.number_of_samples = 20

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

    def set_number_of_samples(self, samples):
        assert isinstance(samples, int)
        self.number_of_samples = samples

    def run_mean_smoothing(self, return_result=False):

        assert len(self.kernel_size) == len(self.dimensions)
        self.data_temp = ndimage.uniform_filter(self.data[:], size=self.kernel_size)

        if return_result:
            return self.data_temp

    def run_gaussian_smoothing(self, return_result=False):
        self.data_temp = ndimage.gaussian_filter(self.data[:], self.kernel_size)

        if return_result:
            return self.data_temp

    def __calculate_entropy(self):


    def __find_sampling_positions(self):
        peaks = numpy.percentile(self.data_temp, 99)
        return numpy.where(self.data_temp >= peaks)


    def calculate_image_quality(self, kernel=None, samples=None):
        """

        """
        if samples is not None:
            self.set_number_of_samples(samples)

        if kernel is not None:
            self.set_smoothing_kernel_size(kernel)

        assert len(self.kernel_size) != 0

        if self.data_temp is None:
            self.run_gaussian_smoothing()

        positions = self.__find_sampling_positions()








