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
    def __init__(self, image, physical=False, verbal=False):

        assert isinstance(image, Image)

        self.data = image

        self.spacing = self.data.get_spacing()
        self.dimensions = self.data.get_dimensions()
        self.physical = physical
        self.verbal = verbal

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

    def __init__(self, image, physical=False, verbal=False):

        Filter.__init__(self, image, physical, verbal)

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
    def __init__(self, image, physical=False, verbal=False):

        Filter.__init__(self, image, physical=physical, verbal=verbal)

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

    def calculate_azimuthal_average(self, bin_size=2, show=False):
        bin_centers, average = radprof.azimuthalAverage(
            self.power,
            binsize=bin_size,
            returnradii=True,
            normalize=True
        )
        dx = self.data.get_spacing()[0]

        f_k = bin_centers*(2.0/(dx*bin_centers.size*bin_size))

        self.average = [f_k, average]

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
        for i in range(len(self.power.shape)):
            sum += numpy.sum(self.power, axis=i)
        zero = floor(float(sum.size)/2)
        sum[zero+1:] = sum[zero+1:]+sum[:zero-1][::-1]
        sum = sum[zero:]

        dx = self.data.get_spacing()[0]

        f_k = numpy.arange(sum.size)*(2.0/(dx*sum.size))

        hf_sum = sum[numpy.where(f_k > .9*f_k.max())]
        print "The mean is: %f" % numpy.mean(hf_sum)
        print "The std is: %f" % numpy.std(hf_sum)


        self.sum = [f_k, sum]

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
        fig, subplots = plt.subplots(1, 3)
        if self.power is not None:
            subplots[0].imshow(numpy.log10(self.power))
        if self.average is not None:
            subplots[1].plot(self.average[0], self.average[1], linewidth=1)
            subplots[1].set_yscale('log')
        if self.sum is not None:
            subplots[2].plot(self.sum[0], self.sum[1], linewidth=1)
            subplots[2].set_yscale('log')

        plt.show()















