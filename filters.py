import numpy
from scipy import ndimage, fftpack
from matplotlib import pyplot as plt
from math import floor

from image import MyImage as Image
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
        self.sum = None
        self.power = None
        self.kernel_size = []

    def set_image(self, image):
        self.data = image

    def calculate_power_spectrum(self, show=False):
        self.power = numpy.abs(fftpack.fftshift(fftpack.fft2(self.data[:])))**2
        if show:
            Image(numpy.log10(self.power), self.spacing).show()

    def calculate_azimuthal_average(self, show=False):
        bin_centers, average = radprof.azimuthalAverage(
            self.power,
            returnradii=True,
            normalize=True
        )
        dx = self.data.get_spacing()[0]


        f_k = bin_centers*(2.0/dx*bin_centers.size)

        self.average = [average, f_k]

        if show:
            plt.plot(numpy.log10(self.average[0]))
            plt.ylabel("Average power")
            plt.xlabel("Frequency")
            plt.show()

    def calculate_summed_power(self, show=False):
        """
        I don't know how "kosher" this method is but here I pack the power spectrum into
        N/2+1 long 1D array, by taking advantage of the fourier spectrum symmetries.
        The highest frequency in the centered power spectrum can be found at all the four
        extremities of the image.
        """

        sum = numpy.zeros(self.power.shape[0])
        for i in range(len(self.power)):
            sum += numpy.sum(self.power, axis=i)
        zero = floor(float(sum.size)/2)
        sum[zero:] = sum[zero:]+sum[:zero-1]
        sum = sum[zero:]

        dx = self.data.get_spacing()[0]

        f_k = numpy.arange(self.sum.size)*(2.0/dx*self.sum.size)

        self.sum = [sum, f_k]

        if show:
            plt.plot(self.sum)
            plt.ylabel("Total power")
            plt.yscale('log')
            plt.xlabel('Frequency')
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

    def show_all(self):
        plots = []
        if self.power is not None:
            plots.append("Power")
        if self.average is not None:
            plots.append("Average")
        if self.sum is not None:
            plots.append("Sum")

        title= ('Power', 'Average', "Sum")
        vals = (self.power, self.average, self.sum)
        color = ('c', 'm', 'g', 'b')

        for i in range(len(title)):
            if i == len(plots):
                i -= 1
            plt.subplot(1, len(plots), i)
            if title[i] in plots:
                plt.plot(vals, linewidth=2, color=color[i])
                plt.title(title[i])
        plt.show()















