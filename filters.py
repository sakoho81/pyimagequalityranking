import numpy
from scipy import ndimage, fftpack
from matplotlib import pyplot as plt

from image import Image
import External.radial_profile as radprof


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
        """
        Mean smoothing is used to create a mask for the entropy calculation
        """

        assert len(self.kernel_size) == len(self.dimensions)
        self.data_temp = ndimage.uniform_filter(self.data[:], size=self.kernel_size)

        if return_result:
            return Image(self.data_temp, self.spacing)

    def calculate_entropy(self):
        # Calculate histogram
        histogram = ndimage.histogram(
            self.data_temp,
            self.data_temp.min(),
            self.data_temp.max(), 50)
        # Exclude zeros
        histogram = histogram[numpy.nonzero(histogram)]
        # Normalize histogram bins to sum to one
        histogram = histogram.astype(float)/histogram.sum()
        return -numpy.sum(histogram*numpy.log2(histogram))

    def find_sampling_positions(self):
        peaks = numpy.percentile(self.data_temp, 85)
        return numpy.where(self.data_temp >= peaks, 1, 0)

    def calculate_image_quality(self, kernel=None, show=False):
        if kernel is not None:
            self.set_smoothing_kernel_size(kernel)

        assert len(self.kernel_size) != 0

        if self.data_temp is None:
            self.run_mean_smoothing()

        positions = self.find_sampling_positions()
        self.data_temp = self.data[:][numpy.nonzero(positions)]

        if show:
            Image(self.data[:]*positions, self.spacing).show()

        return self.calculate_entropy()


class ImageResolution(Filter):
    def __init__(self, image, physical=False):

        Filter.__init__(self, image, physical)

        self.average = None
        self.power = None
        self.kernel_size = []

    def set_image(self, image):
        self.data = image

    def calculate_power_spectrum(self, show=False):
        self.power = numpy.abs(fftpack.fftshift(fftpack.fft2(self.data)))**2
        if show:
            Image(numpy.log10(self.power), self.spacing).show()

    def calculate_azimuthal_average(self, show=False):
        bin_centers, average = radprof.azimuthalAverage(
            self.power,
            returnradii=True,
            normalize=True
        )
        dx = self.data.get_spacing()[0]
        dim = self.data.get_dimensions()[0]

        f_k = 2*bin_centers/(dx*dim)

        self.average = [average, f_k]

        if show:
            plt.plot(f_k, self.average)
            plt.ylabel("Average power")
            plt.xlabel("Frequency")
            plt.show()

    def calculate_image_resolution(self, show_intermediate=False, show=False, measure="quartal"):
        """
        The calculated resolution in the histogram depends on the number of histogram bins. I have to convert
        the bins into physical distances.
        """
        assert self.data is not None, "Please set an image to process"
        self.calculate_power_spectrum(show=show_intermediate)
        self.calculate_azimuthal_average(show=show_intermediate)

        if measure is "quartal":
            pos = numpy.percentile(self.average[0], 75)
            print pos
        else:
            print "Not implemented!!"















